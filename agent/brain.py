"""Agentning "miyasi": Claude bilan suhbat va asboblarni (tools) bajarish sikli."""

from datetime import datetime
from zoneinfo import ZoneInfo

import anthropic

from .config import config
from .memory import Memory

BASE_SYSTEM = """Sen {owner_name} uchun yaratilgan shaxsiy yordamchi agentsan.
Foydalanuvchi bilan u yozgan tilda (odatda o'zbek tilida) qisqa va aniq gaplash.
Foydalanuvchi haqida muhim narsalarni (ism, odatlar, rejalar, afzalliklar) bilib qolsang,
`remember` asbobi bilan saqlab qo'y. Dolzarb ma'lumot kerak bo'lsa, internetdan qidir.

Hozirgacha saqlangan faktlar:
{facts}
"""

TOOLS = [
    {
        "name": "remember",
        "description": "Foydalanuvchi haqidagi muhim faktni uzoq muddatli xotiraga saqlaydi.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"fact": {"type": "string", "description": "Saqlanadigan fakt"}},
            "required": ["fact"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_memories",
        "description": "Xotiradagi barcha faktlarni ID raqamlari bilan qaytaradi.",
        "strict": True,
        "input_schema": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
    },
    {
        "name": "forget",
        "description": "Xotiradan faktni ID raqami bo'yicha o'chiradi.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"fact_id": {"type": "integer"}},
            "required": ["fact_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "current_time",
        "description": "Foydalanuvchi vaqt mintaqasidagi hozirgi sana va vaqtni qaytaradi.",
        "strict": True,
        "input_schema": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
    },
    {"type": "web_search_20260209", "name": "web_search", "max_uses": 5},
    {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 5},
]

# Xavfsizlik klassifikatori so'rovni rad etsa, API uni avtomatik boshqa modelda qayta ishlaydi.
BETAS = ["server-side-fallback-2026-07-01"]
MAX_STEPS = 20


class Brain:
    def __init__(self, memory: Memory, owner_name: str = "egam"):
        self.client = anthropic.AsyncAnthropic()
        self.memory = memory
        self.owner_name = owner_name

    def _system_prompt(self, owner: str) -> str:
        facts = self.memory.facts(owner)
        listed = "\n".join(f"- [{i}] {text}" for i, text in facts) or "- (hali yo'q)"
        return BASE_SYSTEM.format(owner_name=self.owner_name, facts=listed)

    def reset(self, owner: str) -> None:
        """Yangi suhbat boshlaydi. Faktlar snapshot sifatida system promptga yoziladi,
        shuning uchun suhbat davomida prompt o'zgarmaydi va keshdan foydalaniladi."""
        self.memory.new_conversation(owner, self._system_prompt(owner))

    def _run_tool(self, owner: str, name: str, args: dict) -> str:
        if name == "remember":
            fact_id = self.memory.add_fact(owner, args["fact"])
            return f"Saqlandi (ID {fact_id})."
        if name == "list_memories":
            facts = self.memory.facts(owner)
            return "\n".join(f"[{i}] {text}" for i, text in facts) or "Xotira bo'sh."
        if name == "forget":
            ok = self.memory.delete_fact(owner, args["fact_id"])
            return "O'chirildi." if ok else "Bunday ID topilmadi."
        if name == "current_time":
            now = datetime.now(ZoneInfo(config.timezone))
            return now.strftime("%Y-%m-%d %H:%M (%A), ") + config.timezone
        raise ValueError(f"Noma'lum asbob: {name}")

    async def ask(self, owner: str, text: str) -> str:
        conv = self.memory.current_conversation(owner)
        if conv is None or len(self.memory.messages(conv[0])) >= config.max_turns:
            self.reset(owner)
            conv = self.memory.current_conversation(owner)
        conv_id, system_prompt = conv

        self.memory.add_message(conv_id, "user", [{"type": "text", "text": text}])

        for _ in range(MAX_STEPS):
            response = await self.client.beta.messages.create(
                model=config.model,
                max_tokens=16000,
                system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
                messages=self.memory.messages(conv_id),
                tools=TOOLS,
                thinking={"type": "adaptive"},
                output_config={"effort": config.effort},
                betas=BETAS,
                extra_body={"fallbacks": "default"},
            )
            content = [block.model_dump(mode="json", exclude_none=True) for block in response.content]
            self.memory.add_message(conv_id, "assistant", content)

            if response.stop_reason == "refusal":
                return "Kechirasiz, bu so'rovga javob bera olmayman."

            if response.stop_reason == "pause_turn":
                # Server asboblari (qidiruv) uzoq ishladi - davom ettiramiz.
                continue

            if response.stop_reason != "tool_use":
                reply = "".join(b.text for b in response.content if b.type == "text").strip()
                return reply or "(bo'sh javob)"

            results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                try:
                    output = self._run_tool(owner, block.name, block.input)
                    results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
                except Exception as exc:  # asbob xatosi modelga qaytariladi
                    results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": str(exc), "is_error": True}
                    )
            self.memory.add_message(conv_id, "user", results)

        return "Juda ko'p qadam bo'ldi, to'xtadim. Savolni boshqacha so'rab ko'ring."
