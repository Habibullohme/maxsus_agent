#!/usr/bin/env sh
# Commitlar GitHub profilingizdagi yashil katakchalarda ko'rinishi uchun
# git muallifini GitHub akkauntingizga bog'laydi.
# --global: kompyuterdagi barcha loyihalar uchun; aks holda faqat shu repo uchun.
set -e
SCOPE=${1:---local}
git config "$SCOPE" user.name "Habibullohme"
git config "$SCOPE" user.email "121531861+Habibullohme@users.noreply.github.com"
echo "Tayyor: $(git config user.name) <$(git config user.email)>"
