from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# This allows your Ghost site (or any browser) to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Deal(BaseModel):
    name: str
    price: float
    sde: float
    re_val: float = 0

@app.post("/generate-memo")
async def generate_memo(deal: Deal):
    # HICHC Model Constants
    GM_SALARY, DOO_TRANCHE, DOO_RATE = 150000, 200000, 0.12
    MEZZ_RATE, VTB_RATE, MORTGAGE_RATE = 0.10, 0.06, 0.065
    
    # Logic
    mortgage_p = deal.re_val * 0.75
    annual_mortgage = (mortgage_p * MORTGAGE_RATE) if deal.re_val > 0 else 0
    op_price = deal.price - deal.re_val
    mezz_p, vtb_p = op_price * 0.60, op_price * 0.40
    
    mezz_mo = (mezz_p * MEZZ_RATE + DOO_TRANCHE * DOO_RATE) / 12
    vtb_mo = (vtb_p * VTB_RATE / 12) + (vtb_p / 60)
    mortgage_mo = annual_mortgage / 12
    
    total_debt_mo = mezz_mo + vtb_mo + mortgage_mo
    ebitda_mo = (deal.sde - GM_SALARY) / 12
    dscr = ebitda_mo / total_debt_mo
    
    memo = f"HICHC IC MEMO: {deal.name}\n" \
           f"----------------------------\n" \
           f"DSCR: {dscr:.2f}x\n" \
           f"Monthly Net: ${(ebitda_mo - total_debt_mo)*0.89:,.0f}\n" \
           f"Downside Protection: {(1-(1/dscr))*100:.1f}%\n" \
           f"Structure: ${mezz_p:,.0f} Mezz / ${vtb_p:,.0f} VTB"
    
    return {"memo": memo}
