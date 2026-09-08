from app.llm import triage_with_llm


result = triage_with_llm(
    "У меня списали деньги два раза за один заказ"
)

print(result)