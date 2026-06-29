document.addEventListener('DOMContentLoaded', function(){
  var Kituo = lang('Wasambazaji wote','All Vendors');
  let puAttachmentsData = [];
  let puAttFilter = 'all';
  let puAttLayout = 1;

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
    const url = `/salepurchase/vendorStatementData`;
    const data = {data:{tFr,tTo,vendor:st},url};
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

        updateAttachmentsBadge(response.attachment_counts || {}, response.attachments || []);
        puAttachmentsData = response.attachments || [];

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
      // console.error('Error:', error);
    });

    // show loading state
    clearTables();
    showLoadingRows();
    updateAttachmentsBadge({}, []);
    puAttachmentsData = [];


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

    let runningBalance = 0;

    if(rows.length === 0){
      const tr = document.createElement('tr');
      tr.innerHTML = `<td colspan="14">No transactions found for the selected period</td>`;
      tbody.appendChild(tr);
      updateOutstandingBalance(0);
      return;
    }
    rows.forEach(r => {
      const fuelPrice = Number(r.fuel_price) || 0;
      const qty = Number(r.qty) || 0;
      const rawDebt = Number(r.debt) || 0;
      const rawCredit = Number(r.credit) || 0;
      const rowAmount = Number(r.amount) || 0;
      const isPurchase = !!r.use;
      const isPayment = !!r.pay;

      let debtValue = 0;
      let creditValue = 0;

      if(isPurchase){
        debtValue = fuelPrice * qty;
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

      const balanceDisplay = runningBalance > 0
        ? `-${formatNumber(runningBalance)}`
        : formatNumber(Math.abs(runningBalance));
      const transporterDisplay = String(r.transporter || '').trim() ? escapeHtml(r.transporter) : '---';
      const driverDisplay = String(r.driver || '').trim() ? escapeHtml(r.driver) : '---';
      const vehicleDisplay = String(r.vehicle || '').trim() ? escapeHtml(r.vehicle) : '---';
      const fuelDisplay = String(r.fuelN || '').trim() ? escapeHtml(r.fuelN) : '---';

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${moment(r.date).format('DD/MM/YYYY HH:mm')}</td>
        <td>${escapeHtml(r.type||'')}</td>
        <td>${escapeHtml(r.station||'')}</td>
        <td class="text-capitalize">${escapeHtml(r.recorded_by||'')}</td>
        <td>${escapeHtml(r.details||'')}</td>
        <td>${transporterDisplay}</td>
        <td>${driverDisplay}</td>
        <td>${vehicleDisplay}</td>
        <td class="text-right">${fuelDisplay}</td>
        <td class="text-right">${formatNumber(fuelPrice)}</td>
        <td class="text-right">${formatNumber(qty)}</td>
        <td class="text-right">${formatNumber(debtValue)}</td>
        <td class="text-right">${formatNumber(creditValue)}</td>
        <td class="text-right">${balanceDisplay}</td>
      `;
      tbody.appendChild(tr);
    });

    updateOutstandingBalance(runningBalance);

    // get the last row's debt and credit to calculate outstanding balance

  }

  function updateOutstandingBalance(balanceValue){
    const balance = Number(balanceValue) || 0;
    const hasDebt = balance > 0;
    const shownAmount = Math.abs(balance);

    const balanceSpan =` 
                      <strong>${hasDebt?lang('Deni','Debt'):lang('Salio','Balance')}:</strong>
                        <span id="outstandingBalance" class="h5 ${hasDebt ? 'text-danger' : 'green'}">${formatNumber(shownAmount)}</span> <span class="text-primary">${hela}</span>
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
    tx.innerHTML = '<tr><td colspan="14">Loading...</td></tr>';
  }
  function showErrorRows(){
    const fuel = document.querySelector('#fuelSummaryTable tbody');
    fuel.innerHTML = '<tr><td colspan="3">Error loading data</td></tr>';
    // const pay = document.querySelector('#paymentsSummaryTable tbody');
    // pay.innerHTML = '<tr><td colspan="3">Error loading data</td></tr>';
    const tx = document.querySelector('#transactionsTable tbody');
    tx.innerHTML = '<tr><td colspan="14">Error loading data</td></tr>';
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

  function updateAttachmentsBadge(counts, items){
    const btn = document.getElementById('puAttachmentsBtn');
    const countEl = document.getElementById('puAttachmentsCount');
    if(!btn || !countEl) return;

    const invoices = Number(counts.invoices) || 0;
    const receipts = Number(counts.receipts) || 0;
    const total = (items || []).length;

    countEl.textContent = `${invoices} ${lang('ankara','invoice')} | ${receipts} ${lang('risiti','receipt')}`;
    btn.disabled = total === 0;
  }

  function getFilteredAttachments(){
    if(puAttFilter === 'invoice'){
      return puAttachmentsData.filter(a => a.invoice);
    }
    if(puAttFilter === 'receipt'){
      return puAttachmentsData.filter(a => a.receipt);
    }
    return puAttachmentsData.slice();
  }

  function attachmentLabel(att){
    const typeLabel = att.invoice
      ? lang('Ankara','Invoice')
      : lang('Risiti','Receipt');
    const code = att.purchase_code ? `PU-${escapeHtml(att.purchase_code)}` : lang('Manunuzi','Purchase');
    const dateText = att.date ? moment(att.date).format('DD/MM/YYYY HH:mm') : '';
    const vendorText = att.vendor ? escapeHtml(att.vendor) : '';
    return `${code} · ${typeLabel}${dateText ? ` · ${dateText}` : ''}${vendorText ? ` · ${vendorText}` : ''}`;
  }

  function buildAttachmentItemHtml(att){
    const badgeClass = att.invoice ? 'badge-info' : 'badge-success';
    const typeLabel = att.invoice ? lang('Ankara','Invoice') : lang('Risiti','Receipt');
    return `
      <div class="pu-att-item" data-type="${att.invoice ? 'invoice' : 'receipt'}">
        <div class="pu-att-meta">
          <span class="badge ${badgeClass} mr-1">${typeLabel}</span>
          ${attachmentLabel(att)}
        </div>
        <img src="${escapeHtml(att.url)}" alt="${escapeHtml(att.attach_name || typeLabel)}" loading="lazy">
      </div>
    `;
  }

  function renderAttachmentsGallery(){
    const gallery = document.getElementById('puAttachmentsGallery');
    const emptyEl = document.getElementById('puAttachmentsEmpty');
    if(!gallery) return;

    const filtered = getFilteredAttachments();
    gallery.className = `pu-att-gallery layout-${puAttLayout}`;

    if(filtered.length === 0){
      gallery.innerHTML = '';
      if(emptyEl) emptyEl.style.display = 'block';
      return;
    }

    if(emptyEl) emptyEl.style.display = 'none';

    const perPage = Number(puAttLayout) || 1;
    let html = '';
    for(let i = 0; i < filtered.length; i += perPage){
      const pageItems = filtered.slice(i, i + perPage);
      html += `<div class="pu-att-page">${pageItems.map(buildAttachmentItemHtml).join('')}</div>`;
    }
    gallery.innerHTML = html;
  }

  function buildAttachmentsPrintHtml(filtered){
    const perPage = Number(puAttLayout) || 1;
    const durationName = $('#durationSelect').val() || '';
    const heading = `<h4 class="text-center mb-2">${lang('Viambatisho vya Manunuzi','Purchase Attachments')} - ${escapeHtml(durationName)}</h4>
      <p class="text-center small mb-3">${lang('Msambazaji','Vendor')}: ${escapeHtml(Kituo)} · ${filtered.length} ${lang('viambatisho','attachments')} · ${puAttLayout}/${lang('ukurasa','page')}</p>`;

    let pagesHtml = '';
    for(let i = 0; i < filtered.length; i += perPage){
      const pageItems = filtered.slice(i, i + perPage);
      pagesHtml += `<div class="print-page layout-${puAttLayout}">${pageItems.map(att => `
        <div class="print-item">
          <div class="print-meta">${attachmentLabel(att)}</div>
          <img src="${escapeHtml(att.url)}" alt="">
        </div>
      `).join('')}</div>`;
    }

    const printStyles = `
      <style>
        @page { size: A4; margin: 8mm; }
        body { margin: 0; padding: 0; color: #000; font-family: Arial, sans-serif; }
        .print-page { page-break-after: always; box-sizing: border-box; }
        .print-page:last-child { page-break-after: auto; }
        .print-item { box-sizing: border-box; overflow: hidden; }
        .print-meta { font-size: 11px; margin-bottom: 4px; font-weight: 600; }
        .print-item img { width: 100%; object-fit: contain; display: block; background: #fff; }
        .layout-1.print-page { min-height: 277mm; display: flex; flex-direction: column; justify-content: center; }
        .layout-1 .print-item img { max-height: 255mm; }
        .layout-2.print-page { min-height: 277mm; display: grid; grid-template-rows: 1fr 1fr; gap: 6mm; }
        .layout-2 .print-item img { max-height: 125mm; }
        .layout-4.print-page { min-height: 277mm; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 4mm; }
        .layout-4 .print-item img { max-height: 120mm; }
      </style>
    `;

    return printStyles + heading + pagesHtml;
  }

  function setAttachmentFilterButtons(activeFilter){
    $('.pu-att-filter').each(function(){
      const f = $(this).data('filter');
      $(this).removeClass('active btn-secondary btn-outline-secondary btn-outline-info btn-outline-success');
      if(f === activeFilter){
        $(this).addClass('active btn-secondary');
      } else if(f === 'invoice'){
        $(this).addClass('btn-outline-info');
      } else if(f === 'receipt'){
        $(this).addClass('btn-outline-success');
      } else {
        $(this).addClass('btn-outline-secondary');
      }
    });
  }

  $('#puAttachmentsBtn').on('click', function(){
    if($(this).prop('disabled')) return;
    puAttFilter = 'all';
    puAttLayout = 1;
    setAttachmentFilterButtons('all');
    $('.pu-att-layout').removeClass('btn-secondary active').addClass('btn-outline-secondary');
    $('.pu-att-layout[data-layout="1"]').addClass('active btn-secondary').removeClass('btn-outline-secondary');
    $('#puAttachmentsModalDuration').text($('#durationSelect').val() || '');
    renderAttachmentsGallery();
    $('#puAttachmentsModal').modal('show');
  });

  $('.pu-att-filter').on('click', function(){
    puAttFilter = $(this).data('filter') || 'all';
    setAttachmentFilterButtons(puAttFilter);
    renderAttachmentsGallery();
  });

  $('.pu-att-layout').on('click', function(){
    $('.pu-att-layout').removeClass('btn-secondary active').addClass('btn-outline-secondary');
    $(this).addClass('active btn-secondary').removeClass('btn-outline-secondary');
    puAttLayout = Number($(this).data('layout')) || 1;
    renderAttachmentsGallery();
  });

  $('#printPuAttachments').on('click', function(){
    const filtered = getFilteredAttachments();
    if(!filtered.length){
      toastr.info(lang('Hakuna viambatisho vya kuchapisha','No attachments to print'), lang('Taarifa','Info'), {timeOut: 2500});
      return;
    }

    const printWindow = window.open('', '', 'height=800,width=1000');
    if(!printWindow){
      toastr.warning(lang('Kivinjari kimezuia popup ya print. Tafadhali ruhusu popups kisha jaribu tena.','Your browser blocked the print popup. Please allow popups and try again.'));
      return;
    }

    printWindow.document.write(company_header);
    printWindow.document.write(buildAttachmentsPrintHtml(filtered));
    printWindow.document.write('</div></body></html>');
    printWindow.document.close();
    printWindow.focus();
    setTimeout(function(){
      printWindow.print();
      printWindow.close();
    }, 900);
  });

// Print the Report ......//
$('#printStatement').click(function(){
  const customerDetails = document.getElementById('venomerDetails') || document.getElementById('customerDetails');
  const userN = $('#printedBy').val() || 'Admin';
  const duration_name = $('#durationSelect').val() || '';
  const heading = `<h3 class="text-center mb-0" > ${lang('Taarifa ya Msambazaji','Vendor Statement')} ${duration_name} </h3>`
  const statementDetails = `<div class="row my-3">
                            <div class="col-6 row">
                             
                                  
                                <div class="col-5">
                  ${lang('Msambazaji','Vendor')}:  
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

  const reportData = heading + (customerDetails ? customerDetails.outerHTML : '') + statementDetails + theReportData;
     const printWindow = window.open('', '', 'height=600,width=1000');
    printWindow.document.write(company_header);
    printWindow.document.write(`${reportData}`); 
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();

  
});


});