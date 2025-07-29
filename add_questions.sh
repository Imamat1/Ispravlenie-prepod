#!/bin/bash

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MDY5MzkyOX0.LFoP2nGb0MxOcHvbcjspOZve292A90JdigTyNvPqEcs"
TEST_ID="5af02309-e8a1-4bfd-b575-c37faa30e3fd"
URL="https://a72883f7-06a9-42f3-b4a4-18cd6085e38a.preview.emergentagent.com"

# Вопрос 3
curl -X POST "$URL/api/admin/tests/$TEST_ID/questions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "test_id": "'$TEST_ID'",
    "text": "Что произносится в начале намаза?",
    "question_type": "single_choice",
    "options": [
      {"text": "Аллаху Акбар", "is_correct": true},
      {"text": "Субхан Аллах", "is_correct": false},
      {"text": "Ля иляха илля Ллах", "is_correct": false},
      {"text": "Альхамду лилляхи", "is_correct": false}
    ],
    "explanation": "Намаз начинается с произнесения Аллаху Акбар",
    "points": 1,
    "order": 3
  }'

# Вопрос 4
curl -X POST "$URL/api/admin/tests/$TEST_ID/questions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "test_id": "'$TEST_ID'",
    "text": "Как называется поясной поклон в намазе?",
    "question_type": "single_choice", 
    "options": [
      {"text": "Саджда", "is_correct": false},
      {"text": "Руку", "is_correct": true},
      {"text": "Сужуд", "is_correct": false},
      {"text": "Кыям", "is_correct": false}
    ],
    "explanation": "Поясной поклон называется Руку",
    "points": 1,
    "order": 4
  }'

echo "Добавлены вопросы 3 и 4"