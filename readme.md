# Руководство по использованию API

Ниже представлена документация к API, созданному с помощью FastAPI. API содержит один эндпоинт, позволяющий проанализировать финансовые отчёты, переданные клиентом, и получить результат анализа (в том числе с помощью ChatGPT).

## Общая информация

- **Версия OpenAPI**: 3.1.0  
- **Название**: FastAPI  
- **Версия API**: 0.1.0  

## Содержание

1. [Описание эндпоинта /analyze (POST)](#описание-эндпоинта-analyze-post)
2. [Модель RequestModel (структура запроса)](#модель-requestmodel-структура-запроса)
3. [Модель ReportPeriod (элемент массива report)](#модель-reportperiod-элемент-массива-report)
4. [Модель ReportItem (элемент массивов previousPeriodReport и currentPeriodReport)](#модель-reportitem-элемент-массивов-previousperiodreport-и-currentperiodreport)
5. [Пример запроса](#пример-запроса)
6. [Пример ответа](#пример-ответа)
7. [Коды ответа](#коды-ответа)
8. [Валидационные ошибки](#валидационные-ошибки)

---

## Описание эндпоинта `/analyze` (POST)

- **URL**: `/analyze`
- **Метод**: `POST`
- **Назначение**: 
  - Принимает финансовый отчёт от клиента (в формате JSON).
  - Обрабатывает и агрегирует полученные данные.
  - Анализирует их с помощью ChatGPT (через OpenAI).
  - Возвращает результат анализа, оформленный для публикации в Telegram.

### Тело запроса (Request Body)

- **Формат**: `application/json`
- **Схема**: [RequestModel](#модель-requestmodel-структура-запроса)

### Тело ответа (Response Body)

- **Формат**: `application/json`
- **Схема**: объект, содержащий ключ `telegram_post` с HTML-текстом.

Пример:
```json
{
  "telegram_post": "Здесь будет отформатированный в HTML телеграм пост"
}
```

---

## Модель `RequestModel` (структура запроса)

```yaml
RequestModel:
  title: RequestModel
  type: object
  required:
    - report
  properties:
    report:
      title: Report
      type: array
      items:
        $ref: '#/components/schemas/ReportPeriod'
```

**Параметры модели**:

| Поле   | Тип                                                        | Обязательное | Описание                                                    |
|--------|------------------------------------------------------------|--------------|-------------------------------------------------------------|
| report | Массив объектов [`ReportPeriod`](#модель-reportperiod-элемент-массива-report) | да           | Основная структура данных, содержащая период(ы) отчётов.   |

---

## Модель `ReportPeriod` (элемент массива `report`)

```yaml
ReportPeriod:
  title: ReportPeriod
  type: object
  properties:
    previousPeriodReport:
      title: Previousperiodreport
      anyOf:
        - type: array
          items:
            $ref: '#/components/schemas/ReportItem'
        - type: null
    currentPeriodReport:
      title: Currentperiodreport
      anyOf:
        - type: array
          items:
            $ref: '#/components/schemas/ReportItem'
        - type: null
```

**Параметры модели**:

| Поле                | Тип                                                          | Описание                                                                         |
|---------------------|--------------------------------------------------------------|----------------------------------------------------------------------------------|
| previousPeriodReport | Массив объектов [`ReportItem`](#модель-reportitem-элемент-массивов-previousperiodreport-и-currentperiodreport) или `null` | Данные отчётов за предыдущий период. Может быть пустым или отсутствовать (null). |
| currentPeriodReport  | Массив объектов [`ReportItem`](#модель-reportitem-элемент-массивов-previousperiodreport-и-currentperiodreport) или `null` | Данные отчётов за текущий период. Может быть пустым или отсутствовать (null).    |

---

## Модель `ReportItem` (элемент массивов `previousPeriodReport` и `currentPeriodReport`)

```yaml
ReportItem:
  title: ReportItem
  type: object
  required:
    - article
    - realisation
    - sales
    - toTransfer
    - returns
    - costOfSales
    - fines
    - compensationForSubstitutedGoods
    - reimbursementOfTransportationCosts
    - paymentForMarriageAndLostGoods
    - logistics
    - rejectionsAndReturns
    - totalSales
    - tax
    - profit
    - profitWithoutExpense
    - ordersCount
    - returnsCount
    - salesCount
    - refunds
    - storage
    - advertisingExpense
    - advertisingExpenseBonus
    - advertisingExpenseSum
    - commission
    - acceptanceSum
    - cumulative_profit
    - cumulative_realisation
    - profitAbc
    - realisationAbc
    - expense
    - otherDeduction
    - cost
    - averagePriceBeforeSPP
    - averageLogisticsCost
    - averageProfitPerPiece
    - profitability
    - marginality
    - roi
    - averageRedemption
    - drr
    - drrBonus
    - drrSum
    - otherExpense
    - shareInTotalRevenue
    - shareInTotalProfit
    - brand
    - category
    - name
    - vendorCode
    - image
  properties:
    article:
      type: string
      title: Article
    realisation:
      type: number
      title: Realisation
    sales:
      type: number
      title: Sales
    toTransfer:
      type: number
      title: Totransfer
    returns:
      type: number
      title: Returns
    costOfSales:
      type: number
      title: Costofsales
    fines:
      type: number
      title: Fines
    compensationForSubstitutedGoods:
      type: number
      title: Compensationforsubstitutedgoods
    reimbursementOfTransportationCosts:
      type: number
      title: Reimbursementoftransportationcosts
    paymentForMarriageAndLostGoods:
      type: number
      title: Paymentformarriageandlostgoods
    logistics:
      type: number
      title: Logistics
    rejectionsAndReturns:
      type: number
      title: Rejectionsandreturns
    totalSales:
      type: integer
      title: Totalsales
    tax:
      type: number
      title: Tax
    profit:
      type: number
      title: Profit
    profitWithoutExpense:
      type: number
      title: Profitwithoutexpense
    ordersCount:
      type: integer
      title: Orderscount
    returnsCount:
      type: integer
      title: Returnscount
    salesCount:
      type: integer
      title: Salescount
    refunds:
      type: integer
      title: Refunds
    storage:
      type: number
      title: Storage
    advertisingExpense:
      type: number
      title: Advertisingexpense
    advertisingExpenseBonus:
      type: number
      title: Advertisingexpensebonus
    advertisingExpenseSum:
      type: number
      title: Advertisingexpensesum
    commission:
      type: number
      title: Commission
    acceptanceSum:
      type: number
      title: Acceptancesum
    cumulative_profit:
      type: string
      title: Cumulative Profit
    cumulative_realisation:
      type: string
      title: Cumulative Realisation
    profitAbc:
      type: string
      title: Profitabc
    realisationAbc:
      type: string
      title: Realisationabc
    expense:
      type: number
      title: Expense
    otherDeduction:
      type: number
      title: Otherdeduction
    cost:
      type: integer
      title: Cost
    averagePriceBeforeSPP:
      type: number
      title: Averagepricebeforespp
    averageLogisticsCost:
      type: number
      title: Averagelogisticscost
    averageProfitPerPiece:
      type: number
      title: Averageprofitperpiece
    profitability:
      type: number
      title: Profitability
    marginality:
      type: number
      title: Marginality
    roi:
      type: number
      title: Roi
    averageRedemption:
      type: number
      title: Averageredemption
    drr:
      type: number
      title: Drr
    drrBonus:
      type: number
      title: Drrbonus
    drrSum:
      type: number
      title: Drrsum
    otherExpense:
      type: number
      title: Otherexpense
    shareInTotalRevenue:
      type: number
      title: Shareintotalrevenue
    shareInTotalProfit:
      type: number
      title: Shareintotalprofit
    brand:
      type: string
      title: Brand
    category:
      type: string
      title: Category
    name:
      type: string
      title: Name
    vendorCode:
      type: string
      title: Vendorcode
    image:
      type: string
      title: Image
```

Поле `ReportItem` содержит информацию о конкретной позиции товара/артикула за определённый период и его финансовые показатели (продажи, возвраты, логистика, комиссии и т. п.).

---

## Пример запроса

```http
POST /analyze HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "report": [
    {
      "previousPeriodReport": [
        {
          "article": "ART123",
          "realisation": 12000.5,
          "sales": 15000.0,
          "toTransfer": 0,
          "returns": 500.0,
          "costOfSales": 4000.0,
          "fines": 0,
          "compensationForSubstitutedGoods": 0,
          "reimbursementOfTransportationCosts": 0,
          "paymentForMarriageAndLostGoods": 0,
          "logistics": 1000.0,
          "rejectionsAndReturns": 200.0,
          "totalSales": 100,
          "tax": 1500.0,
          "profit": 2500.0,
          "profitWithoutExpense": 3000.0,
          "ordersCount": 120,
          "returnsCount": 20,
          "salesCount": 100,
          "refunds": 2,
          "storage": 200.0,
          "advertisingExpense": 500.0,
          "advertisingExpenseBonus": 100.0,
          "advertisingExpenseSum": 600.0,
          "commission": 300.0,
          "acceptanceSum": 100.0,
          "cumulative_profit": "A",
          "cumulative_realisation": "B",
          "profitAbc": "A",
          "realisationAbc": "B",
          "expense": 1000.0,
          "otherDeduction": 50.0,
          "cost": 100,
          "averagePriceBeforeSPP": 150.0,
          "averageLogisticsCost": 10.0,
          "averageProfitPerPiece": 25.0,
          "profitability": 0.2,
          "marginality": 0.3,
          "roi": 1.5,
          "averageRedemption": 0.8,
          "drr": 50.0,
          "drrBonus": 5.0,
          "drrSum": 55.0,
          "otherExpense": 0,
          "shareInTotalRevenue": 0.1,
          "shareInTotalProfit": 0.15,
          "brand": "BrandA",
          "category": "CategoryA",
          "name": "ProductA",
          "vendorCode": "VC123",
          "image": "http://example.com/imageA.jpg"
        }
      ],
      "currentPeriodReport": [
        {
          "article": "ART123",
          "realisation": 15000.0,
          "sales": 18000.0,
          "toTransfer": 200.0,
          "returns": 400.0,
          "costOfSales": 5000.0,
          "fines": 0,
          "compensationForSubstitutedGoods": 0,
          "reimbursementOfTransportationCosts": 0,
          "paymentForMarriageAndLostGoods": 0,
          "logistics": 1200.0,
          "rejectionsAndReturns": 300.0,
          "totalSales": 120,
          "tax": 1800.0,
          "profit": 2800.0,
          "profitWithoutExpense": 3500.0,
          "ordersCount": 140,
          "returnsCount": 20,
          "salesCount": 120,
          "refunds": 3,
          "storage": 250.0,
          "advertisingExpense": 600.0,
          "advertisingExpenseBonus": 100.0,
          "advertisingExpenseSum": 700.0,
          "commission": 350.0,
          "acceptanceSum": 120.0,
          "cumulative_profit": "A",
          "cumulative_realisation": "A",
          "profitAbc": "A",
          "realisationAbc": "A",
          "expense": 1500.0,
          "otherDeduction": 50.0,
          "cost": 100,
          "averagePriceBeforeSPP": 160.0,
          "averageLogisticsCost": 10.0,
          "averageProfitPerPiece": 30.0,
          "profitability": 0.22,
          "marginality": 0.33,
          "roi": 1.8,
          "averageRedemption": 0.85,
          "drr": 55.0,
          "drrBonus": 5.0,
          "drrSum": 60.0,
          "otherExpense": 0,
          "shareInTotalRevenue": 0.11,
          "shareInTotalProfit": 0.16,
          "brand": "BrandA",
          "category": "CategoryA",
          "name": "ProductA",
          "vendorCode": "VC123",
          "image": "http://example.com/imageA2.jpg"
        }
      ]
    }
  ]
}
```

---

## Пример ответа

```json
{
    "telegram_post": "📊 <b>Еженедельный аналитический отчёт</b>\n🗓 <b>Дата:</b> <i>11-02-2025</i>\n\n---\n\n🔥 <b>Ключевые показатели:</b>\n\n  💰 <i>Прибыль:</i> <b>458437.68</b>₽\n  📉 <i>Выручка:</i> <b>1929966.98</b>₽\n  📊 <i>ROI:</i> <b>48.79%</b>\n\n---\n\n📢 <b>Основные тренды:</b>\nОбщая прибыль снизилась на 13.19%, составив 458437.68 по сравнению с 528224.76 в предыдущем периоде. Выручка упала на 7.98% с 2094693.00 до 1929966.98. ROI увеличился с 50.78% до 48.79%. Основные источники прибыли - респираторы и шайбы крепежные, однако некоторые товары, такие как 'Насадка на плунжерный шприц для смазки', показали отрицательную прибыль в текущем периоде. Ключевыми факторами спада стали снижение объёмов продаж и увеличение убытков.\n\n---\n\n📌 <b>Рекомендации по улучшению:</b>\n\n  📊 <i>Ценообразование:</i> \nРекомендуется провести анализ цен на респираторы, которые составляют значительную долю прибыли, для повышения конкурентоспособности и увеличения объёма продаж.\n\n  📢 <i>Маркетинг:</i> \nУвеличить рекламные бюджеты на респираторы и шайбы крепежные, так как они показали высокий ROI и стабильные продажи.\n\n  🚛 <i>Логистика:</i> \nОптимизировать логистические расходы на товары с высокой стоимостью логистики, такие как 'Насадка на плунжерный шприц для смазки', где убытки превышают прибыль.\n\n---\n\n✅ <b>Итог:</b>\nНужно обратить внимание на товары с отрицательной прибылью, такие как 'Насадка на плунжерный шприц для смазки', и рассмотреть возможность их исключения из ассортимента или улучшения условий продажи. Также следует сосредоточиться на улучшении качества обслуживания клиентов, чтобы снизить возвраты и увеличить удовлетворённость покупателей. Рекомендуется периодически пересматривать ассортимент, основываясь на текущих тенденциях рынка и предпочтениях потребителей.\n\n📍 <i>Отчёт подготовлен командой TrueStats</i>",
  
}
```

> **Примечание:** 
> - Поле `telegram_post` содержит готовый для публикации в Telegram HTML-текст.
> - Точная структура и содержание этого текста зависят от результатов анализа, полученных из ChatGPT.

---

## Коды ответа

- **200 OK** — Успешный ответ. Возвращается объект с полем `telegram_post`.
- **422 Unprocessable Entity** — Ошибка валидации входных данных (см. [Валидационные ошибки](#валидационные-ошибки)).

---

## Валидационные ошибки

API использует встроенную систему валидации FastAPI и возвращает ошибку в формате `HTTPValidationError`, если входные данные не соответствуют описанным схемам.

**Структура ошибки**:

```json
{
  "detail": [
    {
      "loc": ["body", "..."],
      "msg": "Причина ошибки",
      "type": "тип_ошибки"
    }
  ]
}
```

Пример:

```json
{
  "detail": [
    {
      "loc": ["body", "report", 0, "previousPeriodReport", 0, "article"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

Где:
- **loc** — местоположение ошибки (внутри тела запроса, имя поля и т. п.).
- **msg** — сообщение об ошибке.
- **type** — тип ошибки (например, `value_error.missing` или другой).

---

## Заключение

Этот эндпоинт предназначен для обработки и анализа финансовых отчётов. Чтобы получить результат анализа, следует отправить POST‑запрос с корректно сформированным JSON‑телом согласно указанным моделям.  
В случае успешного анализа будет возвращён JSON с ключом `telegram_post`, содержащим HTML-текст, подготовленный для публикации в Telegram.