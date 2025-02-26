from typing import List, Optional
from pydantic import BaseModel


class ReportItem(BaseModel):
    article: str
    realisation: float
    sales: float
    toTransfer: float
    returns: float
    costOfSales: float
    fines: float
    compensationForSubstitutedGoods: float
    reimbursementOfTransportationCosts: float
    paymentForMarriageAndLostGoods: float
    logistics: float
    rejectionsAndReturns: float
    totalSales: int
    tax: float
    profit: float
    profitWithoutExpense: float
    ordersCount: int
    returnsCount: int
    salesCount: int
    refunds: int
    storage: float
    advertisingExpense: float
    advertisingExpenseBonus: float
    advertisingExpenseSum: float
    commission: float
    acceptanceSum: float
    cumulative_profit: str
    cumulative_realisation: str
    profitAbc: str
    realisationAbc: str
    expense: float
    otherDeduction: float
    cost: int
    averagePriceBeforeSPP: float
    averageLogisticsCost: float
    averageProfitPerPiece: float
    profitability: float
    marginality: float
    roi: float
    averageRedemption: float
    drr: float
    drrBonus: float
    drrSum: float
    otherExpense: float
    shareInTotalRevenue: float
    shareInTotalProfit: float
    brand: str
    category: str
    name: str
    vendorCode: str
    image: str


class ReportPeriod(BaseModel):
    previousPeriodReport: Optional[List[ReportItem]] = None
    currentPeriodReport: Optional[List[ReportItem]] = None


class RequestModel(BaseModel):
    report: List[ReportPeriod]
