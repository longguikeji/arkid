# Income calculator

It is convenient to calculate a product sales，Participate in the final price of the income and product of all parties。
<script>

function compute(){

    //Developer
    market_price = document.getElementById("market_price").value
    cost_rate = document.getElementById("cost_rate").value
    income = round(market_price * cost_rate)

    //ArkStore
    market_price_rate = document.getElementById("market_price_rate").value
    cost_price_rate = document.getElementById("cost_price_rate").value

    market_price_rate_price = round(market_price * market_price_rate)
    cost_price_rate_price = round(income * cost_price_rate)
    final_rate_price = Math.min(market_price_rate_price, cost_price_rate_price)

    

    init_level = document.getElementById("init_level").value
    year_all_sell = document.getElementById("year_all_sell").value
    year_level = 1
    if(year_all_sell >= 200)    year_level = 2
    if(year_all_sell >= 400)    year_level = 3
    if(year_all_sell >= 800)    year_level = 4
    if(year_all_sell >= 1600)   year_level = 5
    if(year_all_sell >= 3200)   year_level = 6
    if(year_all_sell >= 6400)   year_level = 7
    if(year_all_sell >= 12800)  year_level = 8
    if(year_all_sell >= 25600)  year_level = 9
    if(year_all_sell >= 51200)  year_level = 10
    

    dl_level = Math.max(init_level, year_level)
    dl_level_rate = round((10-dl_level)*0.1)

    dl_final_rate = Math.max(dl_level_rate, cost_rate)
    dl_final_rate_price = round(market_price * dl_final_rate + final_rate_price)

    dl_rate = document.getElementById("dl_rate").value
    dl_hope_income = round(market_price * dl_rate)

    hope_price = dl_final_rate_price + dl_hope_income
    final_price = Math.min(hope_price, market_price)
    dl_income = final_price - dl_final_rate_price


    document.getElementById("market_price").value = market_price
    document.getElementById("income").value = income

    document.getElementById("market_price_rate_price").value = market_price_rate_price
    document.getElementById("cost_price_rate_price").value = cost_price_rate_price
    document.getElementById("final_rate_price").value = final_rate_price

    document.getElementById("year_level").value = year_level
    document.getElementById("dl_level").value = dl_level
    document.getElementById("dl_level_rate").value = dl_level_rate
    document.getElementById("dl_final_rate").value = dl_final_rate
    document.getElementById("dl_final_rate_price").value = dl_final_rate_price
    document.getElementById("dl_hope_income").value = dl_hope_income

    document.getElementById("hope_price").value = hope_price
    document.getElementById("final_price").value = final_price
    document.getElementById("dl_income").value = dl_income

}

function round(num){
    return Math.round(num * 100)/100
}

</script>


<div class="card">
    <div class="card-header">
        Developer
    </div>
    <form class="card-body row g-3 needs-validation" novalidate>
        <div class="col-md-4">
            <label class="form-label">Market guidance</label>
            <input class="form-control" type="number" id="market_price" min="1" oninput="compute()"></input>
            <div class="form-text">Customizer</div>
        </div>
        <div class="col-md-4">
            <label class="form-label">Cost discount</label>
            <input class="form-control" type="number" max="1" min="0" step="0.01" id="cost_rate" oninput="compute()"></input>
            <div class="form-text">Developer custom</div>
        </div>
        <div class="col-md-4">
            <label class="form-label">income/Cost</label>
            <input class="form-control" id="income" type="number" readOnly="true"></input>
            <div class="form-text">Market guidance * Cost discount</div>
        </div>
    </form>
</div>

<div class="card">
    <div class="card-header">
        ArkStoreplatform
    </div>
    <form class="card-body row g-3 needs-validation" novalidate>
        <div class="col-md-2">
            <label class="form-label">Market price</label>
            <input class="form-control" type="number" id="market_price_rate" value="0.1" readOnly="true"></input>
            <div class="form-text">Fixed value</div>
        </div>
        <div class="col-md-4">
            <label class="form-label">Market price cubing amount</label>
            <input class="form-control" type="number" id="market_price_rate_price" readOnly="true"></input>
            <div class="form-text">Market guidance * Market price</div>
        </div>
        <div class="col-md-2">
            <label class="form-label">Cost price</label>
            <input class="form-control" id="cost_price_rate" type="number" readOnly="true" value="0.3"></input>
            <div class="form-text">Fixed value</div>
        </div>
        <div class="col-md-4">
            <label class="form-label">Cost -priced amount</label>
            <input class="form-control" id="cost_price_rate_price" type="number" readOnly="true"></input>
            <div class="form-text">Cost * Cost price</div>
        </div>
        <div class="col-md-12">
            <label class="form-label">Final cub</label>
            <input class="form-control" id="final_rate_price" type="number" readOnly="true"></input>
            <div class="form-text">Cost -priced amount and Market price cubing amount Minimum value</div>
        </div>
    </form>
</div>

<div class="card">
    <div class="card-header">
        Agent
    </div>
    <form class="card-body row g-3 needs-validation" novalidate>
        <div class="col-md-3">
            <label class="form-label">Initial level</label>
            <input class="form-control" type="number" id="init_level" value="1" max="10" min="1" step="1" oninput="compute()"></input>
            <div class="form-text">Initially 1，Or last year<b>Annual</b>Decide</div>
        </div>
        <div class="col-md-3">
            <label class="form-label">Annual sales</label>
            <input class="form-control" type="number" id="year_all_sell" min="0" oninput="compute()"></input>
            <div class="form-text">This year's market guidance price of all sales products</div>
        </div>
        <div class="col-md-3">
            <label class="form-label">Annual</label>
            <input class="form-control" type="number" id="year_level" readOnly="true"></input>
            <div class="form-text">Determined by annual sales</div>
        </div>
        <div class="col-md-3">
            <label class="form-label">Agent level</label>
            <input class="form-control" id="dl_level" type="number" readOnly="true"></input>
            <div class="form-text">Initial level and Annual The maximum value</div>
        </div>
        <div class="col-md-4">
            <label class="form-label">Level discount</label>
            <input class="form-control" id="dl_level_rate" type="number" readOnly="true"></input>
            <div class="form-text">See：《The corresponding table of the agent level and the level discount》</div>
        </div>
        <div class="col-md-4">
            <label class="form-label">Final discount</label>
            <input class="form-control" id="dl_final_rate" readOnly="true"></input>
            <div class="form-text">Level discount and Cost discount The maximum value</div>
        </div>
        <div class="col-md-4">
            <label class="form-label">Price</label>
            <input class="form-control" id="dl_final_rate_price" readOnly="true"></input>
            <div class="form-text">Market guidance * Final discount + ARKSTORE platform's final commission</div>
        </div>
        <div class="col-md-4">
            <label class="form-label">Proxy discount</label>
            <input class="form-control" id="dl_rate" max="1" min="0" step="0.01" id="cost_rate" value='0.1' oninput="compute()"></input>
            <div class="form-text">Agent custom</div>
        </div>
        <div class="col-md-4">
            <label class="form-label">Agent expected income</label>
            <input class="form-control" id="dl_hope_income" readOnly="true"></input>
            <div class="form-text">Market guidance *  Proxy discount</div>
        </div>
        <div class="col-md-4">
            <label class="form-label">Product expected price</label>
            <input class="form-control" type="number" id="hope_price" readOnly="true"></input>
            <div class="form-text">Price + Agent expected income</div>
        </div>
        <div class="col-md-6">
            <label class="form-label">Product final price</label>
            <input class="form-control" type="number" id="final_price" readOnly="true"></input>
            <div class="form-text">Product expected price and Market guidance Minimize</div>
        </div>
        <div class="col-md-6">
            <label class="form-label">Acting actual income</label>
            <input class="form-control" id="dl_income" readOnly="true"></input>
            <div class="form-text">Product final price - Price</div>
        </div>
    </form>
</div>
