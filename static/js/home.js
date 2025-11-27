       var ISGENERAL = true , ATTENDANTS = 0
       function updateShiftInfo() {
            const now = new Date();
            const hour = now.getHours();
            
            let sessionName;
            let duration;
            let attendants;
            
            // Tuchukulie Shift ya Mchana ni 6:00 AM - 6:00 PM
            if (hour >= 6 && hour < 18) {
                sessionName = "Mchana (Day Shift)";
                duration = "06:00 - 18:00";
                attendants = 5;
            } else {
                sessionName = "Usiku (Night Shift)";
                duration = "18:00 - 06:00";
                attendants = 3;
            }

            const Drange = getDurationRange()
            
            // if(!ISGENERAL) return
            const shiftInfoDiv = document.getElementById('shift-info');
            shiftInfoDiv.innerHTML = `
                <div class="detail-item">
                    <span>${lang('Mpango Zamu','Shift Session')}:</span>
                    <span style="font-weight: bold; color: ${hour >= 6 && hour < 18 ? 'var(--secondary-color)' : '#6c757d'}">${sessionName}</span>
                </div>

                <div class="detail-item">
                    <span>${lang('Muda','Duration')}:</span>
                    <span style="font-weight: bold;">${duration}</span>
                </div>
                <div class="detail-item">
                    <span>${lang('Wahudumu ','Attendants ')}:</span>
                    <span style="font-weight: bold;">${ATTENDANTS}</span>
                </div>
                <div class="detail-item">
                    <span class="bluePrint">${Drange.name}:</span>
                    <span >${moment(Drange.tFr).format('DD/MM/YYYY')} ${!(Drange.name==lang('Leo','Today')) ? `-${moment().format('DD/MM/YYYY')}`:' '}  ${moment().format('HH:mm')}</span>
                </div>
            `;

            
        }

        // Simu ya kwanza na kisha kila sekunde ili kuweka muda upya
        
        // setInterval(updateShiftInfo, 1000);


        // create a function for duration range tha check the active btn-date from home.html and return the duration range
        function getDurationRange() {
            const activeBtn = document.querySelector('.btn-date.active_date'),
            tFr = moment().startOf('day').format(),
            tTo = moment().endOf('day').format();

            if (activeBtn) {
                const range = activeBtn.getAttribute('data-range');
                if (range == 'today') {

                    return {name:lang('Leo','Today'), tFr, tTo };
                }
                if(range=="this_week"){

                    return {name:lang('Wiki Hii','This Week'), tFr: moment().startOf('week').format(), tTo: moment().endOf('week').format() };
                }
                if(range=="this_month"){

                    return {name:lang('Mwezi Huu','This Month'), tFr: moment().startOf('month').format(), tTo: moment().endOf('month').format() };
                }
        }
    }


    const getRData = d =>{
    $('#loadMe').modal('show')
    const {tFr,tTo} = d,
          url = '/analytics/homePageData' ,
          tdy = Number(moment(tTo).format('DD')),
          tmFr = tdy>=7?tFr:moment(moment().subtract(7,'days')).format(),
          data = {data:{tFr:tmFr,tTo},url},
          
          
          sendIt = POSTREQUEST(data)
         
          sendIt.then(resp=>{
              $('#loadMe').modal('hide')
              hideLoading()
            
              if(!resp.success){
                    return toastr.error(lang('Hitilafu imetokea, jaribu tena','Error occured please try again'), lang('Hitilafu','Error'), {timeOut:2000})
              }

              ISGENERAL = resp.general
            //   get a count of unique attendants from resp.pAtt
            const attendantsSet = new Set(resp.pAtt.map(att => att.Incharge_id));
            
                ATTENDANTS = attendantsSet.size

              dashBoard({resp,tFr,tTo})

         
          })

}


const dashBoard = d =>{
    const {sale,expenses,general,isAdmin,Sess,transf,stock,recev,Creditors,Debtors,pAtt,fuelPrice,wastage,tanks,saL} = d.resp
    // update shift info
     const shiftData = () =>{
        if(!ISGENERAL&&Sess?.length){
            const shiftInfoDiv = document.getElementById('shift-info');
            const Ses = Sess[0] || {}
            // get a set of unique attendants from pAtt
            const Drange = getDurationRange()
            shiftInfoDiv.innerHTML = `
                <div class="detail-item">
                    <span>${lang('Mpango Zamu','Shift Session')}:</span>
                    <span style="font-weight: bold; color: ${Ses.shift_name && Ses.shift_name.toLowerCase().includes('mchana') ? 'var(--secondary-color)' : '#6c757d'}">${Ses.shift_name || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span>${lang('Muda','Duration')}:</span>
                    <span style="font-weight: bold;">${Ses.From ? moment(`${Ses.date} ${Ses.From}`).format('HH:mm') : 'N/A'} - ${Ses.To ? moment(`${Ses.date} ${Ses.To}`).format('HH:mm') : 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span>${lang('Wahudumu ','Attendants ')}:</span>
                    <span style="font-weight: bold;">${ATTENDANTS || 0}</span>
                </div>
                <div class="detail-item">
                    <span class="bluePrint">${Drange.name}:</span>
                    <span style="font-weight: bold;">
                      ${moment().format('DD/MM/YYYY')} ${!(Drange.name==lang('Leo','Today')) ? `-${moment().format('DD/MM/YYYY')}`:' '}  ${moment().format('HH:mm')}
                    </span>
                </div>
            `;

        }else{
            updateShiftInfo();
       
     }

     }
     shiftData();

        // update dashboard fuel Sales Price cards from home.html
        const fuelCardsDiv = document.getElementById('fuelPriceData');
        let fp = ``
        fuelPrice.forEach(f => {
            fp += `
                <div class="detail-item">
                            <span class="brown text-capitalize">${f.fuelName}:</span>
                            <span class="fuel-price">${Number(f.newCost || 0).toLocaleString()}</span>
                        </div>
                        
                        <div class="detail-item">

                            <span>${lang('Mwenendo','Trend')}:</span>
                            <span class="fuel-trend ${f.newCost>f.prevCost?'trend-up':'trend-down'}">
                                ${f.prevCost ? `${(((f.newCost - f.prevCost) / f.prevCost) * 100).toFixed(2)}%` : '0%'}
                                
                                ${f.newCost > f.prevCost
                                    ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="5 12 12 5 19 12"></polyline><line x1="12" y1="5" x2="12" y2="19"></line></svg>`
                                    : `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="19 12 12 19 5 12"></polyline><line x1="12" y1="19" x2="12" y2="5"></line></svg>`
                                } 
                            </span>

                        </div>
                    `
        });

        fuelCardsDiv.innerHTML = fp;

        // update dashboard total Sales  cards from home.html
        const salesCardsDiv = document.getElementById('totalSaledata');
        const totalsale = sale.reduce((acc, curr) => acc + Number(curr.amount), 0);
        const paid = sale.reduce((acc, curr) => acc + Number(curr.payed), 0);
        const outstanding = totalsale - paid;
        const sadt = `
         <div class="metric-value">${totalsale.toLocaleString()}</div>

                <div class="sales-metrics">
                    <div class="sales-metric">
                        <span class="metric-label">${lang('Pesa Ilolipwa','Paid Amount')}</span>
                        <div style="font-weight: bold;"><span class="text-primary weight200">${hela}.</span>${paid.toLocaleString()}</div>
                    </div>
                    <div class="sales-metric">
                        <span class="metric-label">${lang('Deni','Outstanding')}</span>
                        <div style="font-weight: bold;"><span class="text-primary weight200">${hela}.</span>${outstanding.toLocaleString()}</div>
                    </div>
                </div>
        `
        salesCardsDiv.innerHTML = sadt;

        // update dashboard Qty of sold fuel cards from home.html
        const qtyCardsDiv = document.getElementById('qtySaledata');
        let qtyHtml = '';
        const theFuel = [...new Set(saL.map(item => item.fuelName))];

        const fuelQtySet = theFuel.map(fuel => {
            const qty_sold = saL.filter(item => item.fuelName === fuel)
                .reduce((acc, curr) => acc + Number(curr.qty_sold), 0);

            return { fuel,  qty_sold };
        });
       
        
        fuelQtySet.forEach(item => {
            qtyHtml += `
                <div class="detail-item">
                    <span class="brown text-capitalize brown">${item.fuel}:</span>
                    <span class="fuel-qty">${Number(item.qty_sold || 0).toLocaleString()}</span>
                </div>
            `;
        });

        // Add detail-item for total
        const totalQty = fuelQtySet.reduce((acc, curr) => acc + Number(curr.qty_sold), 0);
        qtyHtml += `
            <div class="detail-item weight600" style="border-top: 1px solid #ccc; margin-top: 8px; padding-top: 8px;">
                <span class="text-capitalize">${lang('Jumla','Total')}:</span>
                <span class="fuel-qty">${Number(totalQty || 0).toLocaleString()}</span>
            </div>
        `;

       if(saL.length > 0) qtyCardsDiv.innerHTML = qtyHtml;

        // update dashboard Expenses  cards from home.html
        const expCardsDiv = document.getElementById('ExpensesData');
        const fuelExp = expenses.filter(exp => Number(exp.fuel_qty)>0);
        const otherExp = expenses.filter(exp => Number(exp.fuel_qty)===0);

        const expF = fuelExp.reduce((acc, curr) => acc + Number(curr.kiasi), 0);
        const expO = otherExp.reduce((acc, curr) => acc + Number(curr.kiasi), 0);
        const totalExp = expF + expO;

        const expHtml = `
         <div class="detail-item">
                        <span>
                        ${lang('Matumizi ya Mafuta', 'Fuel Usage')} :</span>
                        <span class="smallerFont">${fuelExp.length} ${lang('Rek', 'Recs')} </span> | <span style="font-weight: bold;"> <span class="text-primary weight200">${hela}</span>. ${expF.toLocaleString()}</span>
                    </div>

                    <div class="detail-item">
                        <span> ${lang('Matumizi Mengine', 'Other Expenses')}:</span>
                        <span class="smallerFont">${otherExp.length} ${lang('Rek', 'Recs')} </span> | <span style="font-weight: bold;"><span class="text-primary weight200">${hela}</span>. ${expO.toLocaleString()}</span>
                    </div>

                    <div class="detail-item" style="border-top: 2px solid var(--border-color);">
                        <span style="font-weight: bold;">Jumla ya Matumizi:</span>
                        <span class="smallerFont">${expenses.length} ${lang('Rek', 'Recs')} </span> |
                        <span style="font-weight: bold; color: var(--danger-color);"><span class="text-primary weight200">${hela}</span>. ${totalExp.toLocaleString()}</span>
                    </div>

        `;

       expCardsDiv.innerHTML = expHtml;

        // update dashboard Creditors and debtors from home.html
        const credDebCardsDiv = document.getElementById('creditorsDebtorsData');
        const creditorsTotal = Creditors.reduce((acc, curr) => acc + Number(curr.due), 0);  
        const debtorsTotal = Debtors.reduce((acc, curr) => acc + Number(curr.due), 0);
        const customersCount =  new Set(Debtors.map(item => item.customer_id)).size;
        const suppliersCount =  new Set(Creditors.map(item => item.vendor_id)).size;

        const netBalance = debtorsTotal - creditorsTotal;
      
        const cd = `
        <a href="/salepurchase/customers" class="detail-item">
                        <span> ${lang('Wadaiwa', 'Debtors')} :</span>
                        <span class="smallerFont"> ${lang('Wateja', 'Customers')} ${customersCount} </span> |
                        <span style="font-weight: bold;"> <span class="text-primary weight200">${hela}.</span> ${debtorsTotal.toLocaleString()}</span>
                    </a>

                    <a href="${isAdmin?'/salepurchase/vendors' : '#'}" class="detail-item">
                        <span> ${lang('Wadai', 'Creditors')} :</span>
                        <span class="smallerFont"> ${lang('Wasambazaji', 'Suppliers')} ${suppliersCount.length} </span> |
                        <span style="font-weight: bold; color: var(--danger-color);"><span class="text-primary weight200">${hela}.</span> ${creditorsTotal.toLocaleString()}</span>
                    </a>

                    <div class="detail-item">
                        <span style="font-style: italic;">${lang('Salio la Net Credit', 'Net Credit Balance')}:</span>
                        <span style="font-weight: bold; color: ${netBalance < 0 ? 'var(--danger-color)' : 'var(--secondary-color)'};"><span class="text-primary weight200">${hela}.</span> ${Number(netBalance).toLocaleString()}</span>
                    </div>
        `
        credDebCardsDiv.innerHTML = cd;

        // update dashboard opening stock , stock movement and closing stock from home.html
        const stockCardsDiv = document.getElementById('stockData');
        const StockF = [... new Set(stock.map(itm=>itm.fuelName))]
        // for stock movement we need to calculate the total quanty of fuel opening stock, received, transferred, sales and wastage and closing from stock, recev, transf, saL and wastage respectively 
        const totalOpening = StockF.map(fuel=>{
            opening = stock.filter(s=>s.fuelName===fuel).reduce((acc, curr) => acc + Number(curr.opening), 0)
            current = stock.filter(s=>s.fuelName===fuel).reduce((acc, curr) => acc + Number(curr.closing), 0)
            return {fuel, opening, current}
        })
        const totalReceived = StockF.map(fuel=>{
            received = recev.filter(s=>s.fuelName===fuel).reduce((acc, curr) => acc + Number(curr.qty), 0)
            return {fuel, received}
        })
        const totalTransferred = StockF.map(fuel=>{
            transferred = transf.filter(s=>s.fuelName===fuel).reduce((acc, curr) => acc + Number(curr.qty), 0)
            return {fuel, transferred}
        })
        const totalSales = StockF.map(fuel=>{
            sales = saL.filter(s=>s.fuelName===fuel).reduce((acc, curr) => acc + Number(curr.qty_sold), 0)
            return {fuel, sales}
        })
        const totalWastage = StockF.map(fuel=>{
            wast = wastage.filter(s=>s.fuelName===fuel).reduce((acc, curr) => acc + Number(curr.qty), 0)
            return {fuel, wast}
        })

        const fuelExpenses = StockF.map(fuel=>{
            exp = fuelExp.filter(s=>s.fuelName===fuel&&Number(s.fuel_qty)>0).reduce((acc, curr) => acc + Number(curr.fuel_qty), 0)
            return {fuel, exp}
        })

        let opnFuel = '', recF = '', transF = '', saleF = '', wastF = '', closingF = '', expFl = '';
        totalOpening.forEach(o=>{
            opnFuel += `${Number(o.opening || 0).toLocaleString()} LTRS <span class="bluePrint text-capitalize">${o.fuel}</span> | `
        })
        totalReceived.forEach(r=>{
            recF += `${Number(r.received || 0).toLocaleString()} LTRS <span class="bluePrint text-capitalize">${r.fuel}</span> | `
        })
        totalTransferred.forEach(t=>{
            transF += `${Number(t.transferred || 0).toLocaleString()} LTRS <span class="bluePrint text-capitalize">${t.fuel}</span> | `
        })
        totalSales.forEach(s=>{
            saleF += `${Number(s.sales || 0).toLocaleString()} LTRS <span class="bluePrint text-capitalize">${s.fuel}</span> | `
        })
        totalWastage.forEach(w=>{
            wastF += `${Number(w.wast || 0).toLocaleString()} LTRS <span class="bluePrint text-capitalize">${w.fuel}</span> | `
        })

        totalOpening.forEach(c=>{
            closingF += `${Number(c.current || 0).toLocaleString()} LTRS <span class="bluePrint text-capitalize">${c.fuel}</span> | `
        })

        fuelExpenses.forEach(e=>{
            expFl += `${Number(e.exp || 0).toLocaleString()} LTRS <span class="bluePrint text-capitalize">${e.fuel}</span> | `
        })
     
        let stockHtml = `
                        <div class="detail-item">
                            <span>${lang('Kufungua', 'Opening Stock')}:</span>
                            <span >${opnFuel} </span>  
                        </div>
                        <div class="detail-item">
                            <span>${lang('Kupokea', 'Received')}:</span>
                            <span >${recF} </span>  

                        </div>
                        <div class="detail-item">
                            <span>${lang('Uhamishaji', 'Transfer')}:</span>
                            <span >${transF} </span>  

                        </div>
                        <div class="detail-item">
                            <span>${lang('Mauzo', 'Sales')}:</span>
                            <span >${saleF} </span>  

                        </div>
                        <div class="detail-item">
                            <span>${lang('Upotevu', 'Wastage')}:</span>
                            <span style="font-weight: bold; color: var(--danger-color);">${wastF}</span>
                        </div>
                        <div class="detail-item">
                            <span>${lang('Matumizi ya Mafuta', 'Fuel Expenses')}:</span>
                            <span style="font-weight: bold; color: var(--danger-color);">${expFl}</span>
                        </div>

                        <div class="detail-item" style="border-top: 2px solid var(--border-color);">
                            <span style="font-weight: bold;">${lang('Stock Ilipo', 'Current Stock')}:</span>
                            <span style="font-weight: bold;">${closingF}</span>
                        </div>
        `;

        stockCardsDiv.innerHTML = stockHtml;

}

    $(document).ready(function() {
        getRData(getDurationRange());
           
    });

    $('.btn-date').click(function() {
        $('.btn-date').removeClass('active_date');
        $(this).addClass('active_date');
        getRData(getDurationRange());
    });

    // Refresh  data button
    document.getElementById('refresh-button').addEventListener('click', function() {
        getRData(getDurationRange());
    });