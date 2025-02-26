import json
import logging
import asyncio  # Импортируем asyncio для работы с таймаутами
from datetime import datetime

from openai import AsyncOpenAI

from fastapi import FastAPI, HTTPException
from BaseModels import RequestModel

# Настройка логирования с указанием формата вывода
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Параметры для ChatGPT API
client = AsyncOpenAI(
    api_key="sk-proj-*******"
)
app = FastAPI()


def aggregate_report(report):
    """
    Агрегирует данные отчёта, фильтрует товары с пустым или неопознанным названием,
    суммирует положительную прибыль, убытки (отрицательную прибыль), выручку (sales)
    и вычисляет ROI.
    Возвращает кортеж: (словарь с агрегированными метриками, список отфильтрованных товаров).
    Все итоговые суммы округлены до 2 знаков после запятой.
    """
    logging.info("Начало агрегации отчёта с %d элементами", len(report))
    total_profit = 0.0
    total_losses = 0.0
    total_cost = 0.0
    total_sales = 0.0
    filtered_items = []

    for index, item in enumerate(report, start=1):
        try:
            name = item.name.strip().lower()
        except Exception as e:
            logging.error("Ошибка при обработке названия товара (позиция %d): %s", index, e)
            continue

        if not name or name in ["неопознанный", "неопознан", "пустой"]:
            logging.info("Пропуск товара с неопознанным или пустым названием (позиция %d)", index)
            continue

        try:
            profit = float(item.profit)
            cost = float(item.costOfSales)
            sales = float(item.sales)
        except Exception as e:
            logging.error("Ошибка при конвертации числовых значений для товара '%s' (позиция %d): %s", name, index, e)
            continue

        if profit > 0:
            total_profit += profit
        elif profit < 0:
            total_losses += abs(profit)

        total_cost += cost
        total_sales += sales

        # Добавляем элемент как словарь для дальнейшей сериализации
        filtered_items.append(item.dict())

    roi = round(((total_profit - total_losses) / total_cost * 100), 2) if total_cost != 0 else 0
    aggregated = {
        "totalProfit": round(total_profit, 2),
        "totalLosses": round(total_losses, 2),
        "totalSales": round(total_sales, 2),
        "roi": roi
    }
    logging.info("Агрегация завершена. Результат: %s", aggregated)
    return aggregated, filtered_items


def validate_ai_response(response: dict) -> bool:
    """
    Проверяет, что ответ ИИ содержит все необходимые ключи.
    Ожидаемая структура:
    {
      "analytics": {
        "trendsAndKeyFindings": ""
      },
      "recommendations": {
        "pricingAdjustments": "",
        "adBudgetReview": "",
        "logisticsOptimization": "",
        "otherRecommendations": ""
      }
    }
    """
    required_structure = {
        "analytics": ["trendsAndKeyFindings"],
        "recommendations": ["pricingAdjustments", "adBudgetReview", "logisticsOptimization", "otherRecommendations"]
    }

    for key, subkeys in required_structure.items():
        if key not in response or not isinstance(response[key], dict):
            logging.debug("Ключ '%s' отсутствует или имеет неверный тип.", key)
            return False
        for subkey in subkeys:
            if subkey not in response[key]:
                logging.debug("Ключ '%s' в разделе '%s' отсутствует.", subkey, key)
                return False
    return True


@app.post("/analyze")
async def analyze_report_endpoint(data: RequestModel):
    """
    Асинхронный эндпоинт, который принимает POST‑запрос с финансовым отчётом от клиента,
    агрегирует данные, вызывает ChatGPT (через openai) для анализа и возвращает результат.
    """
    logging.info("Получен запрос на анализ отчёта.")
    try:
        # Извлекаем товары за предыдущий и текущий периоды из списка report
        previous_report = []
        current_report = []
        for period in data.report:
            if period.previousPeriodReport is not None:
                previous_report.extend(period.previousPeriodReport)
            if period.currentPeriodReport is not None:
                current_report.extend(period.currentPeriodReport)
    except Exception as e:
        logging.error("Ошибка при разборе входных данных: %s", e)
        raise HTTPException(status_code=400, detail="Некорректные входные данные")

    try:
        aggregated_previous, filtered_previous = aggregate_report(previous_report)
        aggregated_current, filtered_current = aggregate_report(current_report)
    except Exception as e:
        logging.error("Ошибка при агрегации данных отчёта: %s", e)
        raise HTTPException(status_code=500, detail="Ошибка при агрегации данных отчёта")

    aggregatedMetrics = {
        "previous": aggregated_previous,
        "current": aggregated_current
    }
    logging.info("Сформированы агрегированные метрики: %s", aggregatedMetrics)

    # Формирование системного промпта с требованиями к формату результата
    system_prompt = (
        """Требуется вернуть только один корректный JSON-объект без дополнительного текста. В этом объекте должны присутствовать два основных раздела:

analytics — обобщённая аналитика, сформированная на уровне профессионального анализа. Не используй средние значения, но включи показатели, дающие полезную картину. Обязательно отвечай на русском языке. Анализ должен включать сравнительный динамический анализ (текущий период по отношению к предыдущему) с указанием процентных изменений, если это применимо. Все суммы должны быть округлены до копеек. Исключай из отчёта неопознанные товары, товары с нулевыми показателями, а также объединяй повторяющиеся товары в один итоговый показатель. Необходимо указать:

trendsAndKeyFindings (строка) — описательная часть, где необходимо указать тенденции, ключевые выводы, факторы роста или спада, а также динамику изменений между периодами.
recommendations — список конкретных рекомендаций, построенных на результатах детального анализа, с указанием конкретных товаров, для которых применимы те или иные меры:

pricingAdjustments (строка) — рекомендации по корректировке цен с указанием товаров, где целесообразно изменить ценовую политику.
adBudgetReview (строка) — рекомендации по пересмотру рекламного бюджета, с указанием товаров, требующих увеличения или сокращения расходов на рекламу.
logisticsOptimization (строка) — рекомендации по оптимизации логистических расходов, с упором на товары с негативной прибылью или высокими операционными расходами.
otherRecommendations (строка) — общие выводы по итогам периода и предметные рекомендации повышения эффективности продаж, минимум на 50 слов.

Ниже приведён пример структуры, которую необходимо возвращать (формат JSON менять нельзя):

{
  "analytics": {
    "trendsAndKeyFindings": ""
  },
  "recommendations": {
    "pricingAdjustments": "",
    "adBudgetReview": "",
    "logisticsOptimization": "",
    "otherRecommendations": ""
  }
}
Пожалуйста, выведи только один JSON-объект строго по описанной структуре. Не добавляй никаких пояснений до или после JSON. Если данных нет, указывай 0 или пустые строки."""
    )

    # Формирование пользовательского промпта с данными отчётов
    user_prompt = (
        "Прошу проанализировать следующие входные данные:\n\n"
        "За предыдущий период (json):\n"
        f"Общая прибыль: {aggregatedMetrics['previous']['totalProfit']}\n"
        f"Общие убытки: {aggregatedMetrics['previous']['totalLosses']}\n"
        f"Выручка: {aggregatedMetrics['previous']['totalSales']}\n"
        f"Общий ROI: {aggregatedMetrics['previous']['roi']}\n"
        f"{json.dumps(filtered_previous, ensure_ascii=False)}\n\n"
        "И за текущий период (json):\n"
        f"Общая прибыль: {aggregatedMetrics['current']['totalProfit']}\n"
        f"Общие убытки: {aggregatedMetrics['current']['totalLosses']}\n"
        f"Выручка: {aggregatedMetrics['current']['totalSales']}\n"
        f"Общий ROI: {aggregatedMetrics['current']['roi']}\n"
        f"{json.dumps(filtered_current, ensure_ascii=False)}\n\n"
        "Верни только один JSON-объект, строго соответствующий формату из системного промпта."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Максимальное число попыток получения корректного ответа от ИИ
    max_attempts = 3
    analysis_result = None

    for attempt in range(1, max_attempts + 1):
        try:
            logging.info("Отправка запроса в ChatGPT API (попытка %d/%d)...", attempt, max_attempts)
            # Асинхронный вызов метода API с таймаутом 20 секунд
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    response_format={"type": "json_object"},
                ),
                timeout=20
            )
            response_content = response.choices[0].message.content
            analysis_result = json.loads(response_content)
            logging.info("Получен ответ от ChatGPT API.")
        except asyncio.TimeoutError:
            logging.error("Запрос к ИИ превысил 20 секунд (попытка %d/%d)", attempt, max_attempts)
            if attempt == max_attempts:
                raise HTTPException(status_code=500, detail="Время ожидания ответа от API OpenAI превысило 20 секунд")
            continue
        except Exception as e:
            logging.error("Ошибка при вызове API OpenAI или парсинге JSON (попытка %d/%d): %s", attempt, max_attempts, e)
            if attempt == max_attempts:
                raise HTTPException(status_code=500, detail="Ошибка при вызове API OpenAI или парсинге JSON")
            continue

        if validate_ai_response(analysis_result):
            logging.info("Ответ от ИИ прошёл валидацию.")
            break
        else:
            logging.warning("Ответ от ИИ не содержит всех необходимых данных, повторный запрос (попытка %d/%d)", attempt, max_attempts)
            if attempt == max_attempts:
                raise HTTPException(status_code=500, detail="Модель вернула неполный ответ после нескольких попыток")
            continue

    # Формирование итогового сообщения для Telegram с округлением до копеек
    telegram_post = (
        f"📊 <b>Еженедельный аналитический отчёт</b>\n"
        f"🗓 <b>Дата:</b> <i>{datetime.now().strftime('%d-%m-%Y')}</i>\n\n"
        f"---\n\n"
        f"🔥 <b>Ключевые показатели:</b>\n\n"
        f"  💰 <i>Прибыль:</i> <b>{aggregatedMetrics['current']['totalProfit']}</b>₽\n"
        f"  📉 <i>Выручка:</i> <b>{aggregatedMetrics['current']['totalSales']}</b>₽\n"
        f"  📊 <i>ROI:</i> <b>{aggregatedMetrics['current']['roi']}%</b>\n\n"
        f"---\n\n"
        f"📢 <b>Основные тренды:</b>\n"
        f"{analysis_result.get('analytics', {}).get('trendsAndKeyFindings', '')}\n\n"
        f"---\n\n"
        f"📌 <b>Рекомендации по улучшению:</b>\n\n"
        f"  📊 <i>Ценообразование:</i> \n{analysis_result.get('recommendations', {}).get('pricingAdjustments', '')}\n\n"
        f"  📢 <i>Маркетинг:</i> \n{analysis_result.get('recommendations', {}).get('adBudgetReview', '')}\n\n"
        f"  🚛 <i>Логистика:</i> \n{analysis_result.get('recommendations', {}).get('logisticsOptimization', '')}\n\n"
        f"---\n\n"
        f"✅ <b>Итог:</b>\n{analysis_result.get('recommendations', {}).get('otherRecommendations', '')}\n\n"
        f"📍 <i>Отчёт подготовлен командой TrueStats</i>"
    )
    logging.info("Сформировано итоговое сообщение для Telegram.")

    return {
        "telegram_post": telegram_post
    }


# Для запуска через команду: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn

    logging.info("Запуск сервера FastAPI на http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)