document.addEventListener('DOMContentLoaded', function(){
  var Kituo = lang('Vituo Vyote','All Stations'); 
  const container = document.getElementById('customer_statement');
  if(!container) return;

  const custId = container.dataset.cust || '';
  const durationSelect = document.getElementById('durationSelect');
  const fromDate = document.getElementById('fromDate');
  const toDate = document.getElementById('toDate');
  const stationSelect = document.getElementById('stationSelect');
  const generateBtn = document.getElementById('generateStatement');

  // set default dates to current month
  const now = new Date();
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
  fromDate.value = formatDateISO(firstDay);
  toDate.value = formatDateISO(lastDay);

  // generate previous months and append in #common_duration as .duration-option elements use moment js libray to help with date manipulations

  const commonDuration = document.getElementById('common_duration');
  // get all  12 previous months from this month

  const durations = [
    
    {label: lang('Mwaka Huu','This Year'), value: 'this_year'},
    {label: lang('Mwaka Jana','Last Year'), value: 'last_year'},
  ];



  for(let i = 0; i < 12; i++){
    const month = moment().subtract(i, 'months');
    const label = month.format('MMMM YYYY');
    const value = month.format('YYYY-MM');
    const a = document.createElement('a');
    a.href = '#';
    a.classList.add('dropdown-item');
    a.classList.add('duration-option');
    a.dataset.value = value;
    a.textContent = label;
    commonDuration.appendChild(a);
  }

  durations.forEach(dur => {
    const a = document.createElement('a');
    a.href = '#';
    a.classList.add('duration-option');
    a.classList.add('dropdown-item');
    a.dataset.value = dur.value;
    a.textContent = dur.label;
    commonDuration.innerHTML += a.outerHTML;
  });

  function filters(){
    const tFr = moment(fromDate.value).format();
    const tTo = moment(toDate.value).format();
    const st = parseInt(stationSelect.value) || 0;
    return {tFr,tTo,st};
  }

  $('#common_duration .duration-option').on('click', function(e){
    e.preventDefault();
    const value = $(this).data('value');
    durationSelect.value = $(this).text();
    const now = new Date();
    switch(value){
      case 'last_year':
        const firstDayLastYear = new Date(now.getFullYear() - 1, 0, 1);
        const lastDayLastYear = new Date(now.getFullYear() - 1, 11, 31);
        fromDate.value = formatDateISO(firstDayLastYear);
        toDate.value = formatDateISO(lastDayLastYear);

        break;
      case 'this_year':
        const firstDayYear = new Date(now.getFullYear(), 0, 1);
        const lastDayYear = new Date(now.getFullYear(), 11, 31);
        fromDate.value = formatDateISO(firstDayYear);
        toDate.value = formatDateISO(lastDayYear);
        break;
      default:
          const month = moment(value, 'YYYY-MM');
          if(month.isValid()){
            const firstDayMonth = month.clone().startOf('month');
            const lastDayMonth = month.clone().endOf('month');
            fromDate.value = formatDateISO(firstDayMonth.toDate());
            toDate.value = formatDateISO(lastDayMonth.toDate());
          }
          break;

    }

    $('#durationSelect').val($(this).text());
    fetchAndRender();
  });

  // generate on load
  fetchAndRender();

  generateBtn.addEventListener('click', fetchAndRender);

  function fetchAndRender(){

    const {tFr, tTo, st} = filters();
    const url = `/salepurchase/customerStatementData`;
    const data = {data:{tFr,tTo, station: st,cust: custId},url};
    $('#loadMe').modal('show');
    // console.log(filters());
    const sendIt = POSTREQUEST(data);
    sendIt.then(response => {
      // handle response here
        $('#loadMe').modal('hide');
        hideLoading();
        Kituo = response.kituo || Kituo;
        renderFuelSummary(response.fuel_summary || []);
        renderPaymentsSummary(response.payments_summary || []);
        
        renderTransactions(st?response.transactions.filter(r => (r.st === st||r.st===0)) : response.transactions || []);

        // check whether the duration is not this month, this year or last month then show custom date range in #durationSelect;
        const fromDateObj = moment(tFr);
        const toDateObj = moment(tTo);
        const now = moment();
        const firstDayThisMonth = now.clone().startOf('month');
        const lastDayThisMonth = now.clone().endOf('month');
        const firstDayLastMonth = now.clone().subtract(1, 'month').startOf('month');
        const lastDayLastMonth = now.clone().subtract(1, 'month').endOf('month');
        const firstDayThisYear = now.clone().startOf('year');
        const lastDayThisYear = now.clone().endOf('year');

        if((fromDateObj.isSame(firstDayThisMonth, 'day') && toDateObj.isSame(lastDayThisMonth, 'day')) ||
          (fromDateObj.isSame(firstDayLastMonth, 'day') && toDateObj.isSame(lastDayLastMonth, 'day')) ||
          (fromDateObj.isSame(firstDayThisYear, 'day') && toDateObj.isSame(lastDayThisYear, 'day'))
        ){
          // do nothing, the durationSelect is already set by the dropdown
        }else{
          // set custom date range
          const friendlyFrom = fromDateObj.format('DD/MM/YYYY');
          const friendlyTo = toDateObj.format('DD/MM/YYYY');
            // if the range exactly matches a calendar month, show "MonthName YYYY"
            const startOfMonth = fromDateObj.clone().startOf('month');
            const endOfMonth = fromDateObj.clone().endOf('month');
            if (fromDateObj.isSame(startOfMonth, 'day') && toDateObj.isSame(endOfMonth, 'day')) {
            durationSelect.value = fromDateObj.format('MMMM YYYY');
            } else {
            durationSelect.value = `${friendlyFrom} - ${friendlyTo}`;
            }
        }

    }).catch(error => {
       $('#loadMe').modal('hide');
        hideLoading();
      console.error('Error:', error);
    });

    // show loading state
    clearTables();
    showLoadingRows();


  }

  function renderFuelSummary(rows){
    const tbody = document.querySelector('#fuelSummaryTable tbody');
    tbody.innerHTML = '';
    if(rows.length === 0){
      const tr = document.createElement('tr');
      tr.innerHTML = `<td colspan="3">No fuel consumption data</td>`;
      tbody.appendChild(tr);
      return;
    }
    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
      <td>${escapeHtml(r.fuel || r.name || '')}</td>
      <td class="text-right">${formatNumber(r.avg_price||0)}</td>
      <td class="text-right">${formatNumber(r.qty||0)}</td>
      
      <td class="text-right">${formatNumber(r.amount||0)}</td>
      `;
      tbody.appendChild(tr);
    });

    // Add total row
    const totalQty = rows.reduce((sum, r) => sum + (Number(r.qty) || 0), 0);
    const totalAmount = rows.reduce((sum, r) => sum + (Number(r.amount) || 0), 0);
    const trTotal = document.createElement('tr');
    trTotal.innerHTML = `
      <td><strong>${lang('Jumla', 'Total')}</strong></td>
      <td></td>
      <td class="text-right"><strong>${formatNumber(totalQty)}</strong></td>
      <td class="text-right"><strong>${formatNumber(totalAmount)}</strong></td>
    `;
    tbody.appendChild(trTotal);
  }

  function renderPaymentsSummary(rows){
    const tpaid = document.querySelector('#totalPaidAmount');
   
    tpaid.textContent = formatNumber(rows.reduce((sum, r) => sum + (Number(r.amount) || 0), 0));

  }

  function renderTransactions(rows){
    const tbody = document.querySelector('#transactionsTable tbody');
    tbody.innerHTML = '';
    const {st} = filters();
   

    const last_row = rows[rows.length - 1];
    updateOutstandingBalance(last_row);

    if(rows.length === 0){
      const tr = document.createElement('tr');
      tr.innerHTML = `<td colspan="13">No transactions found for the selected period</td>`;
      tbody.appendChild(tr);
      return;
    }
    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${moment(r.date).format('DD/MM/YYYY HH:mm')}</td>
        <td>${escapeHtml(r.type||'')}</td>
        <td>${r.use?escapeHtml(r.station||''):'-----'}</td>
        <td class="text-capitalize">${r.use?escapeHtml(r.recorded_by||r.user||''):'-----'}</td>
        <td>${r.use?escapeHtml(r.details||''):'-----'}</td>
        <td>${r.use?escapeHtml(r.driver||''):'-----'}</td>
        <td>${r.use?escapeHtml(r.vehicle||''):'-----'}</td>
        
        <td class="text-right">${r.use?escapeHtml(r.fuelN||''):'----'}</td>
        <td class="text-right">${r.use?formatNumber(r.fuel_price||0):'-----'}</td>
        <td class="text-right">${r.use?formatNumber(r.qty||0):'-----'}</td>

        <td class="text-right">${(r.use||r.amount<=0)?formatNumber(r.amount||0):'-----'}</td>
        <td class="text-right">${(!r.use)&&r.amount>0?formatNumber(r.amount||0):'-----'}</td>
      
        <td class="text-right">${Number(r.debt).toFixed(2)>0?'-': ''}${formatNumber(r.debt>0?r.debt:r.credit||0)}</td>
      `;
      tbody.appendChild(tr);
    });

    // get the last row's debt and credit to calculate outstanding balance

  }

  function updateOutstandingBalance(last_row){
    const debt = Number(last_row?.debt) || 0;
    const credit = Number(last_row?.credit) || 0;
   
    const balanceSpan =` 
                      <strong>${debt?lang('Deni','Debt'):lang('Salio','Balance')}:</strong>
                        <span id="outstandingBalance" class="h5 ${debt ? 'text-danger' : 'green'}">${debt?formatNumber(debt):formatNumber(credit)}</span> <span class="text-primary">${hela}</span>
                       `
    $('#deni_au_balance').html(balanceSpan);


  }


  function clearTables(){
    document.querySelectorAll('#fuelSummaryTable tbody,  #transactionsTable tbody').forEach(tb=>tb.innerHTML='');
  }
  function showLoadingRows(){
    const fuel = document.querySelector('#fuelSummaryTable tbody');
    fuel.innerHTML = '<tr><td colspan="3">Loading...</td></tr>';
    // const pay = document.querySelector('#paymentsSummaryTable tbody');
    // pay.innerHTML = '<tr><td colspan="3">Loading...</td></tr>';
    const tx = document.querySelector('#transactionsTable tbody');
    tx.innerHTML = '<tr><td colspan="13">Loading...</td></tr>';
  }
  function showErrorRows(){
    const fuel = document.querySelector('#fuelSummaryTable tbody');
    fuel.innerHTML = '<tr><td colspan="3">Error loading data</td></tr>';
    // const pay = document.querySelector('#paymentsSummaryTable tbody');
    // pay.innerHTML = '<tr><td colspan="3">Error loading data</td></tr>';
    const tx = document.querySelector('#transactionsTable tbody');
    tx.innerHTML = '<tr><td colspan="13">Error loading data</td></tr>';
  }

  function formatNumber(v){
    return Number(v||0).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
  }
  function formatDateISO(d){
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth()+1).padStart(2,'0');
    const dd = String(d.getDate()).padStart(2,'0');
    return `${yyyy}-${mm}-${dd}`;
  }
  function formatDateFriendly(s){
    if(!s) return '';
    const d = new Date(s);
    if(isNaN(d)) return s;
    return d.toLocaleDateString();
  }
  function escapeHtml(text){
    if(text===null||text===undefined) return '';
    return String(text).replace(/[&<>"']/g, function(ch){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[ch];
    });
  }

// Print the Report ......//
$('#printStatement').click(function(){
  const customerDetails = document.getElementById('customerDetails');
  const userN = $('#printedBy').val() || 'Admin';
  const duration_name = $('#durationSelect').val() || '';
  const heading = `<h3 class="text-center mb-0" > ${lang('Taarifa ya Mteja','Customer Statement')} ${duration_name} </h3>`
  const statementDetails = `<div class="row my-3">
                            <div class="col-6 row">
                             
                                  
                                <div class="col-5">
                                    ${lang('Kituo','Station')}:  
                                </div>
                                <div class="col-7 ">
                                    ${Kituo}  
                                </div>
                                  
                                <div class="col-5">
                                    ${lang('Imetolewa','Issued on')}:  
                                </div>
                                <div class="col-7 ">
                                    ${moment().format('DD/MM/YYYY HH:mm')}  
                                </div>

                                <div class="col-5">
                                    ${lang('Imetolewa na','Issued by')}:  
                                </div>
                                <div class="col-7 text-capitalize">
                                    ${userN}    
                                </div>

                            </div>


                     </div>           
  `
  const theReportData = document.getElementById('TheReportData').innerHTML;
  // document.body.innerHTML = heading + customerDetails.outerHTML + statementDetails + theReportData;

  const reportData = heading + customerDetails.outerHTML + statementDetails + theReportData;
     const printWindow = window.open('', '', 'height=600,width=1000');
    printWindow.document.write(company_header);
    printWindow.document.write(`${reportData}`); 
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();

  
});


});



