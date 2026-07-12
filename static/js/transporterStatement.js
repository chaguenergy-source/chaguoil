document.addEventListener('DOMContentLoaded', function(){
  var Kituo = lang('Wasafirishaji wote','All Transporters');

  const container = document.getElementById('customer_statement');
  if(!container) return;

  const durationSelect = document.getElementById('durationSelect');
  const fromDate = document.getElementById('fromDate');
  const toDate = document.getElementById('toDate');
  const stationSelect = document.getElementById('stationSelect');
  const generateBtn = document.getElementById('generateStatement');

  const now = new Date();
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
  fromDate.value = formatDateISO(firstDay);
  toDate.value = formatDateISO(lastDay);

  const commonDuration = document.getElementById('common_duration');
  const durations = [
    {label: lang('Mwaka Huu','This Year'), value: 'this_year'},
    {label: lang('Mwaka Jana','Last Year'), value: 'last_year'},
  ];

  for(let i = 0; i < 12; i++){
    const month = moment().subtract(i, 'months');
    const a = document.createElement('a');
    a.href = '#';
    a.classList.add('dropdown-item', 'duration-option');
    a.dataset.value = month.format('YYYY-MM');
    a.textContent = month.format('MMMM YYYY');
    commonDuration.appendChild(a);
  }

  durations.forEach(dur => {
    const a = document.createElement('a');
    a.href = '#';
    a.classList.add('dropdown-item', 'duration-option');
    a.dataset.value = dur.value;
    a.textContent = dur.label;
    commonDuration.innerHTML += a.outerHTML;
  });

  function filters(){
    return {
      tFr: moment(fromDate.value).format(),
      tTo: moment(toDate.value).format(),
      st: parseInt(stationSelect.value) || 0
    };
  }

  $('#common_duration .duration-option').on('click', function(e){
    e.preventDefault();
    const value = $(this).data('value');
    durationSelect.value = $(this).text();
    const n = new Date();

    if(value === 'last_year'){
      fromDate.value = formatDateISO(new Date(n.getFullYear() - 1, 0, 1));
      toDate.value = formatDateISO(new Date(n.getFullYear() - 1, 11, 31));
    } else if(value === 'this_year'){
      fromDate.value = formatDateISO(new Date(n.getFullYear(), 0, 1));
      toDate.value = formatDateISO(new Date(n.getFullYear(), 11, 31));
    } else {
      const month = moment(value, 'YYYY-MM');
      if(month.isValid()){
        fromDate.value = formatDateISO(month.clone().startOf('month').toDate());
        toDate.value = formatDateISO(month.clone().endOf('month').toDate());
      }
    }

    $('#durationSelect').val($(this).text());
    fetchAndRender();
  });

  fetchAndRender();
  generateBtn.addEventListener('click', fetchAndRender);

  function fetchAndRender(){
    const {tFr, tTo, st} = filters();
    const data = {data:{tFr,tTo,transporter:st},url:'/salepurchase/transporterStatementData'};

    $('#loadMe').modal('show');
    clearTables();
    showLoadingRows();

    POSTREQUEST(data).then(response => {
      $('#loadMe').modal('hide');
      hideLoading();

      Kituo = response.kituo || Kituo;
      renderFuelSummary(response.fuel_summary || []);
      renderPaymentsSummary(response.payments_summary || []);
      renderTransactions(st ? (response.transactions || []).filter(r => (r.st === st || r.st === 0)) : (response.transactions || []));
    }).catch(() => {
      $('#loadMe').modal('hide');
      hideLoading();
      showErrorRows();
    });
  }

  function renderFuelSummary(rows){
    const tbody = document.querySelector('#fuelSummaryTable tbody');
    tbody.innerHTML = '';
    if(rows.length === 0){
      tbody.innerHTML = '<tr><td colspan="4">No fuel consumption data</td></tr>';
      return;
    }

    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${escapeHtml(r.fuel || '')}</td>
        <td class="text-right">${formatNumber(r.avg_price || 0)}</td>
        <td class="text-right">${formatNumber(r.qty || 0)}</td>
        <td class="text-right">${formatNumber(r.amount || 0)}</td>
      `;
      tbody.appendChild(tr);
    });

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
    let runningBalance = 0;

    if(rows.length === 0){
      tbody.innerHTML = '<tr><td colspan="14">No transactions found for the selected period</td></tr>';
      updateOutstandingBalance(0);
      return;
    }

    rows.forEach(r => {
      const fuelPrice = Number(r.fuel_price) || 0;
      const qty = Number(r.qty) || 0;
      const rowAmount = Number(r.amount) || 0;
      const rawDebt = Number(r.debt) || 0;
      const rawCredit = Number(r.credit) || 0;
      const isPurchase = !!r.use;
      const isPayment = !!r.pay;

      let debtValue = 0;
      let creditValue = 0;

      if(isPurchase){
        debtValue = rowAmount;
      } else if(isPayment){
        creditValue = rowAmount;
      } else {
        debtValue = rawDebt;
        creditValue = rawCredit;
      }

      if(typeof r.balance !== 'undefined' && r.balance !== null){
        runningBalance = Number(r.balance) || 0;
      } else {
        runningBalance = runningBalance + debtValue - creditValue;
      }

      const balanceDisplay = runningBalance > 0 ? `-${formatNumber(runningBalance)}` : formatNumber(Math.abs(runningBalance));

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${moment(r.date).format('DD/MM/YYYY HH:mm')}</td>
        <td>${escapeHtml(r.type||'')}</td>
        <td>${escapeHtml(r.station||'')}</td>
        <td class="text-capitalize">${escapeHtml(r.recorded_by||'')}</td>
        <td>${escapeHtml(r.details||'')}</td>
        <td>${escapeHtml(r.transporter||'---')}</td>
        <td>${escapeHtml(r.driver||'---')}</td>
        <td>${escapeHtml(r.vehicle||'---')}</td>
        <td class="text-right">${escapeHtml(r.fuelN||'---')}</td>
        <td class="text-right">${formatNumber(fuelPrice)}</td>
        <td class="text-right">${formatNumber(qty)}</td>
        <td class="text-right">${formatNumber(debtValue)}</td>
        <td class="text-right">${formatNumber(creditValue)}</td>
        <td class="text-right">${balanceDisplay}</td>
      `;
      tbody.appendChild(tr);
    });

    updateOutstandingBalance(runningBalance);
  }

  function updateOutstandingBalance(balanceValue){
    const balance = Number(balanceValue) || 0;
    const hasDebt = balance > 0;
    const shownAmount = Math.abs(balance);
    const balanceSpan = `
      <strong>${hasDebt ? lang('Deni','Debt') : lang('Salio','Balance')}:</strong>
      <span id="outstandingBalance" class="h5 ${hasDebt ? 'text-danger' : 'green'}">${formatNumber(shownAmount)}</span>
      <span class="text-primary">${hela}</span>
    `;
    $('#deni_au_balance').html(balanceSpan);
  }

  function clearTables(){
    document.querySelectorAll('#fuelSummaryTable tbody, #transactionsTable tbody').forEach(tb => tb.innerHTML = '');
  }

  function showLoadingRows(){
    document.querySelector('#fuelSummaryTable tbody').innerHTML = '<tr><td colspan="4">Loading...</td></tr>';
    document.querySelector('#transactionsTable tbody').innerHTML = '<tr><td colspan="14">Loading...</td></tr>';
  }

  function showErrorRows(){
    document.querySelector('#fuelSummaryTable tbody').innerHTML = '<tr><td colspan="4">Error loading data</td></tr>';
    document.querySelector('#transactionsTable tbody').innerHTML = '<tr><td colspan="14">Error loading data</td></tr>';
  }

  function formatDateISO(d){
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth()+1).padStart(2,'0');
    const dd = String(d.getDate()).padStart(2,'0');
    return `${yyyy}-${mm}-${dd}`;
  }

  function escapeHtml(text){
    if(text===null||text===undefined) return '';
    return String(text).replace(/[&<>"']/g, function(ch){
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch];
    });
  }

  $('#printStatement').click(function(){
    const details = document.getElementById('trspDetails') || document.getElementById('venomerDetails');
    const userN = $('#printedBy').val() || 'Admin';
    const durationName = $('#durationSelect').val() || '';

    const heading = `<h3 class="text-center mb-0">${lang('Taarifa ya Msafirishaji','Transporter Statement')} ${durationName}</h3>`;
    const statementDetails = `
      <div class="row my-3">
        <div class="col-6 row">
          <div class="col-5">${lang('Msafirishaji','Transporter')}:</div>
          <div class="col-7">${Kituo}</div>
          <div class="col-5">${lang('Imetolewa','Issued on')}:</div>
          <div class="col-7">${moment().format('DD/MM/YYYY HH:mm')}</div>
          <div class="col-5">${lang('Imetolewa na','Issued by')}:</div>
          <div class="col-7 text-capitalize">${userN}</div>
        </div>
      </div>
    `;

    const reportBody = document.getElementById('TheReportData').innerHTML;
    openAndPrintDocument(reportData);
  });
});
