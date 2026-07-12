let flowData = [];
let activeDetail = null;
let activeDayDetail = null;

const endpoint = (window.dailySalesConfig || {}).endpoint || '/salepurchase/getDailySalesActivity';
const dayDetailEndpoint = (window.dailySalesConfig || {}).dayDetailEndpoint || '/salepurchase/getDailySalesDayDetail';
const currency = (window.dailySalesConfig || {}).currency || '';
const filters = () => {
    const st = Number($('#stationFilter').val() || 0);
    const today = { rname: lang('Leo', 'Today'), tFr: moment().startOf('day').format(), tTo: moment().format() };
    const week = { rname: lang('Wiki hii', 'This Week'), tFr: moment().startOf('isoWeek').format(), tTo: moment().format() };
    const month = { rname: lang('Mwezi huu', 'This Month'), tFr: moment().startOf('month').format(), tTo: moment().format() };
    return { st, today, week, month };
};

const filterDaysByStation = (days, st) => (st ? (days || []).filter(d => Number(d.st) === st) : (days || []));

const sumDays = days => {
    const totals = {
        day_count: new Set((days || []).map(d => d.date)).size,
        sales_amount: 0,
        credit_sales_amount: 0,
        cash_payment_amount: 0,
        mobile_amount: 0,
        total_received: 0,
        loss_bonus: 0,
        flow_qty: 0,
        flow_amount: 0,
        dep_before_amount: 0,
        cash_dep_amount: 0,
        expenses_amount: 0,
        transfer_qty: 0,
        transfer_worth: 0,
        receive_qty: 0,
        receive_worth: 0
    };
    (days || []).forEach(d => {
        totals.sales_amount += Number(d.sales_amount || 0);
        totals.credit_sales_amount += Number(d.credit_sales_amount || 0);
        totals.cash_payment_amount += Number(d.cash_payment_amount || 0);
        totals.mobile_amount += Number(d.mobile_amount || 0);
        totals.total_received += Number(d.total_received || 0);
        totals.loss_bonus += Number(d.loss_bonus || 0);
        totals.flow_qty += Number(d.flow_qty || 0);
        totals.flow_amount += Number(d.flow_amount || 0);
        totals.dep_before_amount += Number(d.dep_before_amount || 0);
        totals.cash_dep_amount += Number(d.cash_dep_amount || 0);
        totals.expenses_amount += Number(d.expenses_amount || 0);
        totals.transfer_qty += Number(d.transfer_qty || 0);
        totals.transfer_worth += Number(d.transfer_worth || 0);
        totals.receive_qty += Number(d.receive_qty || 0);
        totals.receive_worth += Number(d.receive_worth || 0);
    });
    return totals;
};

const lossBonusCell = val => {
    const n = Number(val || 0);
    if (Math.abs(n) < 0.0001) return formatNumber(0);
    const cls = n > 0 ? 'text-danger' : 'text-success';
    const label = n > 0 ? lang('Hasara', 'Loss') : lang('Bonusi', 'Bonus');
    return `<span class="${cls}">${formatNumber(Math.abs(n))}</span><span class="sub-label">${label}</span>`;
};

const amountCell = (amount, count) => {
    const amt = formatNumber(amount || 0);
    if (!count) return `<span class="text-muted">—</span>`;
    return `${amt}<span class="sub-label">${count} ${lang('rekodi', 'records')}</span>`;
};

const flowCell = (qty, amount) => `${formatNumber(qty || 0)} L<span class="sub-label">${formatNumber(amount || 0)}</span>`;

const qtyWorthCell = (qty, worth, count) => {
    if (!count) return `<span class="text-muted">—</span>`;
    return `${formatNumber(qty || 0)} L<span class="sub-label">${formatNumber(worth || 0)} · ${count} ${lang('rekodi', 'records')}</span>`;
};

const loadRecords = ({ tFr, tTo, rname, init }) => {
    $('#loadMe').modal('show');
    const req = POSTREQUEST({ data: { tFr, tTo }, url: endpoint });

    req.then(res => {
        $('#loadMe').modal('hide');
        hideLoading();
        if (res.success) {
            renderRecords({ resp: res, rname, init, tFr, tTo });
        } else {
            toastr.error(lang(res.swa, res.eng), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
        }
    }).catch(() => {
        $('#loadMe').modal('hide');
        hideLoading();
        toastr.error(lang('Tatizo la mtandao, jaribu tena', 'Network error, try again'), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
    });
};

$(document).ready(() => {
    const { month } = filters();
    loadRecords({ ...month, init: 1 });
});

const renderRecords = ({ resp, rname, init, tFr, tTo }) => {
    const { today, week } = filters();

    if (init) {
        addDurationRecords({ days: resp.days, ...today });
        addDurationRecords({ days: resp.days, ...week });
    }

    addDurationRecords({ days: resp.days, tFr, tTo, rname });
    renderSummary();
};

const addDurationRecords = ({ days, tFr, tTo, rname }) => {
    const isThere = flowData.find(d => d.tFr === tFr && d.tTo === tTo && d.rname === rname);
    if (isThere) return;

    const tFrDate = moment(tFr).format('YYYY-MM-DD');
    const tToDate = moment(tTo).format('YYYY-MM-DD');
    const filtered = (days || []).filter(d => d.date >= tFrDate && d.date <= tToDate);

    flowData.push({
        id: flowData.length + 1,
        rname,
        tFr,
        tTo,
        days: filtered
    });
};

function createArray(rname, tFr, tTo) {
    const parent = flowData.find(d => d.tFr <= tFr && d.tTo >= tTo);
    const isThere = flowData.find(d => d.tFr === tFr && d.tTo === tTo);

    if (isThere) {
        toastr.info(lang('tayari ipo', 'already exists'), lang('Taarifa', 'Info'), { timeOut: 2000 });
        return;
    }

    if (parent) {
        addDurationRecords({ days: parent.days, tFr, tTo, rname });
        renderSummary();
    } else {
        loadRecords({ tFr, tTo, rname, init: 0 });
    }
}

const renderSummary = () => {
    const { st } = filters();
    let tr = '';

    flowData.forEach(d => {
        const days = filterDaysByStation(d.days, st);
        const t = sumDays(days);

        tr += `<tr class="smallFont cursor-pointer moreDetails" data-report="${d.id}">
            <td><a type="button" class="bluePrint moreDetails" data-report="${d.id}">${d.rname}</a></td>
            <td>${t.day_count}</td>
            <td>${flowCell(t.flow_qty, t.flow_amount)}</td>
            <td>${formatNumber(t.receive_qty)} L<br><span class="sub-label">${formatNumber(t.receive_worth)}</span></td>
            <td>${formatNumber(t.transfer_qty)} L<br><span class="sub-label">${formatNumber(t.transfer_worth)}</span></td>
            <td>${formatNumber(t.sales_amount)}</td>
            <td>${formatNumber(t.credit_sales_amount)}</td>
            <td>${formatNumber(t.expenses_amount)}</td>
            <td>${formatNumber(t.cash_payment_amount)}</td>
            <td>${formatNumber(t.mobile_amount)}</td>
            <td>${formatNumber(t.dep_before_amount)}</td>
            <td>${formatNumber(t.cash_dep_amount)}</td>
            <td>${formatNumber(t.total_received)}</td>
            <td>${lossBonusCell(t.loss_bonus)}</td>
        </tr>`;
    });

    $('#activitySummaryBody').html(tr);
};

$('body').on('click', '.moreDetails', function () {
    const id = Number($(this).data('report'));
    const data = flowData.find(d => d.id === id);
    if (!data) return;
    activeDetail = data;
    renderDetails(data);
});

$('#backToSummary').on('click', function () {
    $('#paymentDayDetail').hide();
    $('#paymentDetails').hide();
    $('#paymentSummary').show();
    activeDayDetail = null;
});

$('#backToDayList').on('click', function () {
    $('#paymentDayDetail').hide();
    $('#paymentDetails').show();
    activeDayDetail = null;
});
const renderDetails = data => {
    const { st } = filters();
    const rows = filterDaysByStation(data.days, st);
    const title = lang('Maelezo ya Mauzo Kilasiku - ', 'Daily Sales Details - ');

    let tr = '';
    rows.forEach((r, idx) => {
        tr += `<tr class="smallFont day-detail-row" data-date="${r.date}" data-st="${r.st}" data-stn="${escapeDailyHtml(r.stN || '')}">
            <td>${idx + 1}</td>
            <td>${moment(r.date).format('DD/MM/YYYY')}</td>
            <td>${r.stN || ''}</td>
            <td>${flowCell(r.flow_qty, r.flow_amount)}</td>
            <td>${qtyWorthCell(r.receive_qty, r.receive_worth, r.receive_count)}</td>
            <td>${qtyWorthCell(r.transfer_qty, r.transfer_worth, r.transfer_count)}</td>
            <td>${formatNumber(r.sales_amount || 0)}</td>
            <td>${amountCell(r.credit_sales_amount, r.credit_sales_count)}</td>
            <td>${amountCell(r.expenses_amount, r.expenses_count)}</td>
            <td>${amountCell(r.cash_payment_amount, r.cash_payment_count)}</td>
            <td>${amountCell(r.mobile_amount, r.mobile_count)}</td>
            <td>${amountCell(r.dep_before_amount, r.dep_before_count)}</td>
            <td>${amountCell(r.cash_dep_amount, r.cash_dep_count)}</td>
            <td>${formatNumber(r.total_received || 0)}</td>
            <td>${lossBonusCell(r.loss_bonus)}</td>
        </tr>`;
    });

    const t = sumDays(rows);
    tr += `<tr class="smallFont font-weight-bold">
        <td colspan="3">${lang('Jumla', 'Total')}</td>
        <td>${formatNumber(t.flow_qty)} L / ${formatNumber(t.flow_amount)}</td>
        <td>${formatNumber(t.receive_qty)} L / ${formatNumber(t.receive_worth)}</td>
        <td>${formatNumber(t.transfer_qty)} L / ${formatNumber(t.transfer_worth)}</td>
        <td>${formatNumber(t.sales_amount)}</td>
        <td>${formatNumber(t.credit_sales_amount)}</td>
        <td>${formatNumber(t.expenses_amount)}</td>
        <td>${formatNumber(t.cash_payment_amount)}</td>
        <td>${formatNumber(t.mobile_amount)}</td>
        <td>${formatNumber(t.dep_before_amount)}</td>
        <td>${formatNumber(t.cash_dep_amount)}</td>
        <td>${formatNumber(t.total_received)}</td>
        <td>${lossBonusCell(t.loss_bonus)}</td>
    </tr>`;

    $('#activityDetailsTitle').html(title + `<span class="bluePrint">${data.rname}</span>`);
    $('#activityDetailsBody').html(tr);
    $('#paymentSummary').hide();
    $('#paymentDayDetail').hide();
    $('#paymentDetails').show();
};

const escapeDailyHtml = text => {
    if (text === null || text === undefined) return '';
    return String(text).replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
};

const fmtDt = val => (val ? moment(val).format('DD/MM/YYYY HH:mm') : '—');
const sumField = (rows, field) => (rows || []).reduce((a, b) => a + Number(b[field] || 0), 0);

const buildMiniTable = ({ headers, rows, footer }) => {
    if (!rows || !rows.length) return '';
    const body = rows.map(cells => `<tr>${cells.map(c => `<td>${c}</td>`).join('')}</tr>`).join('');
    const foot = footer ? `<tfoot><tr>${footer.map(c => `<td>${c}</td>`).join('')}</tr></tfoot>` : '';
    return `<div class="table-responsive daily-table-scroll"><table class="daily-mini-table daily-scroll-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${body}</tbody>${foot}</table></div>`;
};

const buildSection = (title, bodyHtml, cssClass = '') => {
    if (!bodyHtml) return '';
    return `<div class="daily-section ${cssClass}"><div class="daily-section-title">${title}</div><div class="daily-section-body">${bodyHtml}</div></div>`;
};

const buildPumpFuelBlock = fuel => {
    const analogNote = fuel.analog_used
        ? `<span class="daily-analog-tag">${lang('Analogi', 'Analog')}</span>` : '';
    const rows = (fuel.pumps || []).map(p => `
      <tr${p.analog_used ? ' class="analog-pump-row"' : ''}>
        <td>${escapeDailyHtml(p.station_name)}</td>
        <td>${escapeDailyHtml(p.pump_name)}${p.analog_used ? ` <span class="daily-analog-tag daily-analog-tag-sm">${lang('Analogi', 'Analog')}</span>` : ''}</td>
        <td>${formatNumber(p.initial)}</td>
        <td>${formatNumber(p.final)}</td>
        <td>${formatNumber(p.price)}</td>
        <td>${formatNumber(p.qty)}</td>
        <td>${formatNumber(p.amount)}</td>
      </tr>`).join('');

    return `
      <div class="daily-pump-title brown weight500 mb-1">${lang('Pampu za', 'Pumps of')} <u>${escapeDailyHtml(fuel.fuel_name)}</u>${analogNote}</div>
      <div class="table-responsive daily-table-scroll daily-pump-scroll-wrap">
      <table class="daily-mini-table daily-pump-table daily-scroll-table mb-2">
        <thead>
          <tr>
            <th>${lang('Dispensa', 'Dispenser')}</th>
            <th>${lang('Pampu', 'Pump')}</th>
            <th>${lang('Kufungua', 'Opening')}</th>
            <th>${lang('Kufunga', 'Closing')}</th>
            <th>${lang('Bei', 'Price')}</th>
            <th>${lang('Flow', 'Flow')} (L)</th>
            <th>${lang('Kiasi', 'Amount')}</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
        <tfoot>
          <tr>
            <td colspan="5">${lang('Jumla', 'Total')}</td>
            <td>${formatNumber(fuel.total_qty)}</td>
            <td>${formatNumber(fuel.total_amount)}</td>
          </tr>
        </tfoot>
      </table>
      </div>`;
};

const buildShiftAttachmentsBlock = shift => {
    const items = shift.attachments || [];
    if (!items.length) return '';
    const cards = items.map(att => {
        const label = att.printed_doc
            ? lang('Dok. iliyosainiwa', 'Signed document')
            : escapeDailyHtml(att.name || lang('Picha', 'Photo'));
        const thumb = att.is_image && att.url
            ? `<img src="${escapeDailyHtml(att.url)}" alt="${escapeDailyHtml(att.name || '')}" class="daily-attach-img" loading="lazy">`
            : `<div class="daily-attach-file-fallback">${lang('Faili', 'File')}</div>`;
        return `
          <a href="${escapeDailyHtml(att.url || '#')}" target="_blank" class="daily-attach-card" title="${escapeDailyHtml(att.name || '')}">
            <div class="daily-attach-thumb">${thumb}</div>
            <div class="daily-attach-meta">
              <div class="daily-attach-name">${label}</div>
              <div class="daily-attach-sub">${fmtDt(att.date)} · ${escapeDailyHtml(att.by || '')}</div>
            </div>
          </a>`;
    }).join('');
    return `
      <div class="daily-shift-attachments mt-2">
        <div class="daily-attach-heading">${lang('Viambatanisho', 'Attachments')} (${items.length})</div>
        <div class="daily-attach-grid">${cards}</div>
      </div>`;
};

const buildShiftSummaryBlock = summary => {
    const s = summary || {};
    const cur = currency ? ` (${escapeDailyHtml(currency)})` : '';
    const row = (label, qty, amount, bold = false) => {
        const tag = bold ? 'th' : 'td';
        const cls = bold ? ' class="daily-summary-grey"' : '';
        return `<tr${cls}><${tag}${cls}>${label}</${tag}><${tag}${cls}>${qty !== '' ? formatNumber(qty) : ''}</${tag}><${tag}${cls}>${amount !== '' ? formatNumber(amount) : ''}</${tag}></tr>`;
    };
    let body = row(lang('Mafuta yaliyotoka', 'Fuel Flow'), s.flow_qty, s.flow_amount, true);
    if (Number(s.sale_qty) > 0) body += row(lang('Mauzo Wateja Maalum', 'Credit Order Sales'), s.sale_qty, s.sale_amount);
    if (Number(s.transfer_qty) > 0) body += row(lang('Mafuta yaliyosafirishwa', 'Transferred Fuel'), s.transfer_qty, s.transfer_amount);
    if (Number(s.expense_fuel_qty) > 0) body += row(lang('Mafuta Yaliyotumika', 'Fuel Usage'), s.expense_fuel_qty, s.expense_fuel_amount);
    if (Number(s.sale_qty) > 0 || Number(s.transfer_qty) > 0 || Number(s.expense_fuel_qty) > 0) {
        body += row(lang('Mauzo ya Pampu(Cash)', 'Cash Pump Sales'), s.pump_sale_qty, s.pump_sale_amount, true);
    }
    if (Number(s.expense_cash) > 0) body += row(lang('Matumizi ya Pesa', 'Expenses by Cash'), '', s.expense_cash);
    if (Number(s.cash_before) > 0) body += row(lang('Cash Iliyowekwa Benki', 'Cash Deposit'), '', s.cash_before);
    body += row(lang('Pesa Inayotakiwa', 'Net Required Amount'), '', s.required, true);
    body += row(lang('Pesa Iliyolipwa', 'Paid Amount'), '', s.paid, true);
    if (s.is_loss) body += row(lang('Hasara', 'Loss'), '', s.loss_profit, true);
    else if (s.is_bonus) body += row(lang('Bonusi', 'Bonus'), '', s.loss_profit, true);
    else body += row(lang('Bonusi/Hasara', 'Bonus/Loss'), '', s.loss_profit, true);
    return `
      <div class="daily-shift-summary mt-2">
        <div class="daily-pump-title weight500 mb-1">${lang('Ufupisho wa Zamu', 'Shift Summary Report')}</div>
        <table class="daily-mini-table daily-shift-summary-table">
          <thead>
            <tr>
              <th>${lang('Jumla', 'Total')}</th>
              <th>${lang('Kiasi', 'Qty')} <span class="text-primary">LTRS</span></th>
              <th>${lang('Kiasi', 'Amount')}${cur ? `<span class="text-primary">${cur}</span>` : ''}</th>
            </tr>
          </thead>
          <tbody>${body}</tbody>
        </table>
      </div>`;
};

const buildShiftCard = shift => {
    const analogBadge = shift.analog_used
        ? `<span class="daily-analog-tag daily-analog-tag-shift">${lang('Mita ya Analogi', 'Analog Readings')}</span>` : '';
    const fuelsHtml = (shift.fuels || []).map(buildPumpFuelBlock).join('');
    return `
      <div class="daily-shift-card${shift.analog_used ? ' analog-shift-card' : ''}">
        <table class="daily-mini-table daily-shift-meta-table mb-2">
          <tbody>
            <tr>
              <td><strong>${lang('Mhusika wa Pampu', 'Pump Attendant')}:</strong> ${escapeDailyHtml(shift.attendant || '—')}</td>
              <td><strong>${lang('Zamu', 'Shift')}:</strong> <a href="/salepurchase/viewShift?i=${shift.id}">SHF-${escapeDailyHtml(shift.code || shift.id)}</a>${analogBadge}</td>
            </tr>
            <tr>
              <td><strong>${lang('Meneja / Aliyerekodi', 'Manager / Recorded by')}:</strong> ${escapeDailyHtml(shift.manager || '—')}</td>
              <td><strong>${lang('Muda', 'Time')}:</strong> ${fmtDt(shift.from_dt)} — ${fmtDt(shift.to_dt)}</td>
            </tr>
          </tbody>
        </table>
        ${fuelsHtml || `<div class="daily-empty-note">${lang('Hakuna vipimo vya pampu', 'No pump readings')}</div>`}
        ${shift.summary ? buildShiftSummaryBlock(shift.summary) : ''}
        <table class="daily-mini-table daily-sign-table mt-2">
          <tbody>
            <tr>
              <td>${lang('Mhusika wa Pampu', 'Pump Attendant')}: ${escapeDailyHtml(shift.attendant || '')}<br>${lang('Sahihi', 'Signature')}: ....................</td>
              <td>${lang('Meneja wa Kituo', 'Station Manager')}: ${escapeDailyHtml(shift.manager || '')}<br>${lang('Sahihi', 'Signature')}: ....................</td>
            </tr>
          </tbody>
        </table>
        ${buildShiftAttachmentsBlock(shift)}
      </div>`;
};

const buildShiftsSection = sessions => {
    if (!(sessions || []).length) {
        return buildSection(lang('1. Zamu za Wahusika wa Pampu', '1. Pump Attendant Shifts'),
            `<p class="daily-empty-note mb-0">${lang('Hakuna zamu zilizofunguliwa siku hii', 'No shifts opened on this day')}</p>`,
            'daily-section-shifts');
    }
    const body = sessions.map(session => `
      <div class="daily-session-group">
        <div class="daily-session-head">
          ${escapeDailyHtml(session.session_name)} · ${escapeDailyHtml(session.time_from)} — ${escapeDailyHtml(session.time_to)}
          · ${(session.shifts || []).length} ${lang('zamu', 'shifts')}
          · <a href="/salepurchase/SessionView?i=${session.id}">SessionView</a>
          <span class="badge ${session.complete ? 'badge-success' : 'badge-warning'} ml-1">${session.complete ? lang('Imekamilika', 'Complete') : lang('Haijakamilika', 'Incomplete')}</span>
        </div>
        ${(session.shifts || []).map(buildShiftCard).join('') || `<div class="daily-empty-note">${lang('Hakuna zamu kwa session hii', 'No shifts in this session')}</div>`}
      </div>`).join('');
    return buildSection(lang('1. Zamu za Wahusika wa Pampu', '1. Pump Attendant Shifts'), body, 'daily-section-shifts');
};

const buildSalesTable = rows => buildMiniTable({
    headers: [
        lang('Tarehe', 'Date'),
        lang('Session', 'Session'),
        lang('Zamu', 'Shift'),
        lang('Mhusika', 'Attendant'),
        lang('Ankara', 'Invoice'),
        lang('Mteja', 'Customer'),
        lang('Mafuta', 'Fuel'),
        lang('Bei', 'Price'),
        lang('Kiasi L', 'Qty L'),
        lang('Thamani', 'Amount'),
    ],
    rows: (rows || []).map(r => [
        fmtDt(r.sale_dt),
        escapeDailyHtml(r.session_name || '—'),
        r.linked_shift_id
            ? `<a href="/salepurchase/viewShift?i=${r.linked_shift_id}">SHF-${escapeDailyHtml(r.shift_code || r.linked_shift_id)}</a>`
            : '—',
        escapeDailyHtml(r.attendant || '—'),
        r.sale_id
            ? `<a href="/salepurchase/viewFuelSales?i=${r.sale_id}">${escapeDailyHtml(r.sale_code || '')}</a>`
            : escapeDailyHtml(r.sale_code || '—'),
        escapeDailyHtml(r.cust_name || '—'),
        escapeDailyHtml(r.fuel_name || ''),
        formatNumber(r.sa_price),
        formatNumber(r.qty_sold),
        formatNumber(r.amount),
    ]),
    footer: [
        lang('Jumla', 'Total'),
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        formatNumber(sumField(rows, 'qty_sold')),
        formatNumber(sumField(rows, 'amount')),
    ],
});

const buildCustomerPayTable = rows => buildMiniTable({
    headers: [
        lang('Tarehe', 'Date'),
        lang('Session', 'Session'),
        lang('Zamu', 'Shift'),
        lang('Mteja', 'Customer'),
        lang('Oda', 'Order'),
        lang('Akaunti', 'Account'),
        lang('Mhusika', 'Attendant'),
        lang('Kiasi', 'Amount'),
    ],
    rows: (rows || []).map(r => [
        fmtDt(r.tarehe),
        escapeDailyHtml(r.session_name || '—'),
        r.shift_id
            ? `<a href="/salepurchase/viewShift?i=${r.shift_id}">SHF-${escapeDailyHtml(r.shift_code || r.shift_id)}</a>`
            : '—',
        escapeDailyHtml(r.cust_name || '—'),
        escapeDailyHtml(r.order_code || '—'),
        escapeDailyHtml(r.account_name || '—'),
        escapeDailyHtml(r.attendant || '—'),
        formatNumber(r.Amount),
    ]),
    footer: [
        lang('Jumla', 'Total'),
        '',
        '',
        '',
        '',
        '',
        '',
        formatNumber(sumField(rows, 'Amount')),
    ],
});

const buildMobilePayTable = rows => buildMiniTable({
    headers: ['#', lang('Session', 'Session'), lang('Tarehe', 'Date'), lang('Mteja', 'Customer'), lang('Akaunti', 'Account'), lang('Mhusika', 'Attendant'), lang('Kiasi', 'Amount')],
    rows: (rows || []).map((r, i) => [i + 1, escapeDailyHtml(r.session_name || ''), fmtDt(r.tarehe), escapeDailyHtml(r.cust_name || r.cust_label || '—'), escapeDailyHtml(r.account_name || ''), escapeDailyHtml(r.attendant || '—'), formatNumber(r.Amount)]),
    footer: [lang('Jumla', 'Total'), '', '', '', '', '', formatNumber(sumField(rows, 'Amount'))],
});

const buildCashDepTable = rows => buildMiniTable({
    headers: ['#', lang('Aina', 'Type'), lang('Session', 'Session'), lang('Tarehe', 'Date'), lang('Akaunti', 'Account'), lang('Na', 'By'), lang('Kiasi', 'Amount')],
    rows: (rows || []).map((r, i) => {
        const typeLabel = r.deposit_type === 'bank'
            ? lang('Benki', 'Bank')
            : lang('Kabla ya Zamu', 'Before Shift');
        return [i + 1, typeLabel, escapeDailyHtml(r.session_name || r.stN || '—'), fmtDt(r.tarehe), escapeDailyHtml(r.account_name || ''), escapeDailyHtml(r.by || r.attendant || '—'), formatNumber(r.Amount)];
    }),
    footer: [lang('Jumla', 'Total'), '', '', '', '', '', formatNumber(sumField(rows, 'Amount'))],
});

const buildTransferTable = rows => buildMiniTable({
    headers: ['#', lang('Session', 'Session'), lang('Noti', 'Note'), lang('Mafuta', 'Fuel'), lang('Kutoka', 'From'), lang('Kwenda', 'To'), lang('Kiasi L', 'Qty L'), lang('Thamani', 'Worth'), lang('Mhusika', 'Attendant')],
    rows: (rows || []).map((r, i) => [
        i + 1, escapeDailyHtml(r.session_name || ''),
        r.transfer_id ? `<a href="/salepurchase/viewTransfer?i=${r.transfer_id}">TFR-${escapeDailyHtml(r.transfer_code || '')}</a>` : '—',
        escapeDailyHtml(r.fuel_name || ''), escapeDailyHtml(r.from_tank || ''), escapeDailyHtml(r.to_tank || ''),
        formatNumber(r.qty), formatNumber(r.worth), escapeDailyHtml(r.attendant || '—'),
    ]),
    footer: [lang('Jumla', 'Total'), '', '', '', '', '', formatNumber(sumField(rows, 'qty')), formatNumber(sumField(rows, 'worth')), ''],
});

const buildReceiveTable = rows => buildMiniTable({
    headers: ['#', lang('Session', 'Session'), lang('Noti', 'Note'), lang('Mafuta', 'Fuel'), lang('Tanki', 'Tank'), lang('Kiasi L', 'Qty L'), lang('Thamani', 'Worth')],
    rows: (rows || []).map((r, i) => [
        i + 1, escapeDailyHtml(r.session_name || ''),
        r.receive_id ? `<a href="/salepurchase/viewFuelReceive?i=${r.receive_id}">TTR-${escapeDailyHtml(r.receive_code || '')}</a>` : '—',
        escapeDailyHtml(r.fuel_name || ''), escapeDailyHtml(r.to_tank || ''),
        formatNumber(r.qty), formatNumber(r.worth),
    ]),
    footer: [lang('Jumla', 'Total'), '', '', '', '', formatNumber(sumField(rows, 'qty')), formatNumber(sumField(rows, 'worth'))],
});

const expenseTypeLabel = r => {
    if (r.exp_paye) {
        const base = lang('Mshahara', 'Salary');
        return r.salary_advance
            ? `${base} (${lang('Malipo ya awali ya mshahara', 'Salary Advance')})`
            : base;
    }
    return r.exp_name || '';
};

const buildExpenseTable = rows => buildMiniTable({
    headers: ['#', lang('Aina', 'Type'), lang('Tarehe', 'Date'), lang('Aliyekabidhiwa', 'Given To'), lang('Mhusika', 'Attendant'), lang('Aliyerekodi', 'Recorded By'), lang('Kiasi', 'Amount'), lang('Mafuta L', 'Fuel L')],
    rows: (rows || []).map((r, i) => [
        i + 1,
        escapeDailyHtml(expenseTypeLabel(r)),
        fmtDt(r.tarehe),
        escapeDailyHtml(r.given_to || '—'),
        escapeDailyHtml(r.attendant || '—'),
        escapeDailyHtml(r.recorded_by || '—'),
        formatNumber(r.kiasi),
        formatNumber(r.fuel_qty),
    ]),
    footer: [lang('Jumla', 'Total'), '', '', '', '', '', formatNumber(sumField(rows, 'kiasi')), formatNumber(sumField(rows, 'fuel_qty'))],
});

const evalDash = '—';

const buildStockEvaluationSection = stock => {
    const s = stock || {};
    const tanks = s.tanks || [];
    const showFlow = !!s.all_complete;
    const showDetail = !!(s.has_adj || s.all_complete);
    const showStick = !!(s.has_adj && s.all_complete);
    const flowCell = v => (showFlow ? formatNumber(v) : evalDash);
    const detailCell = v => (showDetail && showFlow ? formatNumber(v) : evalDash);
    const stickCell = v => (showStick ? formatNumber(v) : evalDash);
    const diffCell = (v) => {
        if (!showStick) return evalDash;
        const cls = Number(v) < 0 ? 'text-danger weight600' : 'weight600';
        return `<span class="${cls}">${formatNumber(v)}</span>`;
    };
    if (!tanks.length) {
        return buildSection(
            lang('11. Mwenendo wa Stoku kwa Siku', '11. Day Stock Evaluation'),
            `<p class="daily-empty-note mb-0">${lang('Hakuna data ya stoku', 'No stock data')}</p>`,
            'daily-section-eval',
        );
    }
    const rows = tanks.map((t, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${escapeDailyHtml(t.tank_name || '')}</td>
        <td>${escapeDailyHtml(t.fuel_name || '')}</td>
        <td>${showDetail ? formatNumber(t.bses) : evalDash}</td>
        <td>${flowCell(t.ses_flow)}</td>
        <td>${showDetail ? formatNumber(t.a_flow) : evalDash}</td>
        <td>${flowCell(t.rcq)}</td>
        <td>${showDetail ? formatNumber(t.read) : evalDash}</td>
        <td>${stickCell(t.stick)}</td>
        <td>${diffCell(t.diff)}</td>
      </tr>`).join('');
    const table = `
      <div class="table-responsive daily-table-scroll">
        <table class="daily-mini-table daily-eval-wide-table daily-scroll-table">
          <thead>
            <tr>
              <th>#</th>
              <th>${lang('Tanki', 'Tank')}</th>
              <th>${lang('Mafuta', 'Fuel')}</th>
              <th>${lang('Kiasi/Kabla', 'Qty/Before')} (L)</th>
              <th>${lang('Yaliyotoka', 'Flow')} (L)</th>
              <th>${lang('Baada/Zamu', 'After/Flow')} (L)</th>
              <th>${lang('Kupokea', 'Receive')} (L)</th>
              <th>${lang('Kiasi/Baada', 'Qty/After')} (L)</th>
              <th>${lang('Stiki', 'Stick')} (L)</th>
              <th>${lang('Tofauti', 'Diff')} (L)</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
    return buildSection(lang('11. Mwenendo wa Stoku kwa Siku', '11. Day Stock Evaluation'), table, 'daily-section-eval');
};

const buildFuelFlowSummarySection = fuelFlow => {
    const ff = fuelFlow || {};
    const rows = ff.rows || [];
    const t = ff.totals || {};
    const cur = currency ? ` (${escapeDailyHtml(currency)})` : '';
    if (!rows.length) {
        return buildSection(
            lang('9. Ufupisho Mwenendo wa Mafuta yaliyotoka', '9. Total Day Fuel Flow Summary'),
            `<p class="daily-empty-note mb-0">${lang('Hakuna data ya mafuta', 'No fuel flow data')}</p>`,
            'daily-section-eval',
        );
    }
    const body = rows.map((r, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${escapeDailyHtml(r.fuel_name || '')}</td>
        <td>${formatNumber(r.price)}</td>
        <td>${formatNumber(r.flow_q)}</td><td>${formatNumber(r.flow_a)}</td>
        <td>${formatNumber(r.tr_q)}</td><td>${formatNumber(r.tr_a)}</td>
        <td>${formatNumber(r.exp_q)}</td><td>${formatNumber(r.exp_a)}</td>
        <td>${formatNumber(r.sa_q)}</td><td>${formatNumber(r.sa_a)}</td>
        <td>${formatNumber(r.pmp_q)}</td><td>${formatNumber(r.pmp_a)}</td>
      </tr>`).join('');
    const table = `
      <div class="table-responsive daily-table-scroll">
        <table class="daily-mini-table daily-eval-wide-table daily-scroll-table">
          <thead>
            <tr>
              <th rowspan="2">#</th>
              <th rowspan="2">${lang('Mafuta', 'Fuel')}</th>
              <th rowspan="2">${lang('Bei', 'Price')}${cur}</th>
              <th colspan="2">${lang('Yaliyotoka', 'Flow')}</th>
              <th colspan="2">${lang('Kusafirisha', 'Transfer')}</th>
              <th colspan="2">${lang('Matumizi ya mafuta', 'Fuel Expenses')}</th>
              <th colspan="2">${lang('Mauzo/Maalum', 'Custom/Sales')}</th>
              <th colspan="2">${lang('Mauzo/Pampu (Cash)', 'Cash Pump Sales')}</th>
            </tr>
            <tr>
              <th>${lang('Kiasi', 'Qty')} (L)</th><th>${lang('Thamani', 'Amount')}</th>
              <th>${lang('Kiasi', 'Qty')} (L)</th><th>${lang('Thamani', 'Amount')}</th>
              <th>${lang('Kiasi', 'Qty')} (L)</th><th>${lang('Thamani', 'Amount')}</th>
              <th>${lang('Kiasi', 'Qty')} (L)</th><th>${lang('Thamani', 'Amount')}</th>
              <th>${lang('Kiasi', 'Qty')} (L)</th><th>${lang('Thamani', 'Amount')}</th>
            </tr>
          </thead>
          <tbody>${body}
            <tr class="daily-summary-grey">
              <td colspan="3">${lang('Jumla', 'Total')}</td>
              <td>${formatNumber(t.flow_q)}</td><td>${formatNumber(t.flow_a)}</td>
              <td>${formatNumber(t.tr_q)}</td><td>${formatNumber(t.tr_a)}</td>
              <td>${formatNumber(t.exp_q)}</td><td>${formatNumber(t.exp_a)}</td>
              <td>${formatNumber(t.sa_q)}</td><td>${formatNumber(t.sa_a)}</td>
              <td>${formatNumber(t.pmp_q)}</td><td>${formatNumber(t.pmp_a)}</td>
            </tr>
          </tbody>
        </table>
      </div>`;
    return buildSection(lang('9. Ufupisho Mwenendo wa Mafuta yaliyotoka', '9. Total Day Fuel Flow Summary'), table, 'daily-section-eval');
};

const buildPumpPaymentsSummarySection = pay => {
    const p = pay || {};
    const cur = currency ? ` (${escapeDailyHtml(currency)})` : '';
    const totPaid = Number(p.tot_paid || 0);
    const totReq = Number(p.tot_req || 0);
    const totLpr = Math.abs(Number(p.tot_lpr || 0));
    let bonusLossRow = '';
    if (totPaid > totReq) {
        bonusLossRow = `<tr class="daily-summary-green"><th>${lang('Bonasi', 'Bonus')}</th><th>${formatNumber(totLpr)}</th></tr>`;
    } else if (totPaid < totReq) {
        bonusLossRow = `<tr class="daily-summary-loss"><th>${lang('Hasara', 'Loss')}</th><th>${formatNumber(totLpr)}</th></tr>`;
    }
    const table = `
      <table class="daily-mini-table daily-pump-pay-table">
        <thead>
          <tr><th>${lang('Jumla', 'Total')}</th><th>${lang('Kiasi', 'Amount')}${cur}</th></tr>
        </thead>
        <tbody>
          <tr class="daily-summary-grey"><th>${lang('Mauzo ya pampu (Cash)', 'Cash Pump Sales')}</th><th>${formatNumber(p.tot_psa)}</th></tr>
          <tr><td>${lang('Matumizi ya Cash', 'Cash Expenses')}</td><td>${formatNumber(p.tot_exp)}</td></tr>
          <tr><td>${lang('Pesa Iliyowekwa Benki', 'Cash Deposit')}</td><td>${formatNumber(p.tot_cab)}</td></tr>
          <tr class="daily-summary-grey"><th>${lang('Pesa Inayotakiwa', 'Net Required Amount')}</th><th>${formatNumber(p.tot_req)}</th></tr>
          <tr class="daily-summary-grey"><th>${lang('Pesa Ilolipwa', 'Net Paid')}</th><th>${formatNumber(p.tot_paid)}</th></tr>
          ${bonusLossRow}
        </tbody>
      </table>`;
    return buildSection(
        lang('10. Ufupisho Mauzo ya Pampu na Malipo', '10. Total Day Pump Sales & Payments Summary'),
        table,
        'daily-section-eval daily-section-pump-pay',
    );
};

const buildEvaluationSections = evaluations => {
    const ev = evaluations || {};
    return [
        buildFuelFlowSummarySection(ev.fuel_flow),
        buildPumpPaymentsSummarySection(ev.pump_payments),
        buildStockEvaluationSection(ev.stock),
    ].join('');
};

const buildActivityTablesSection = tables => {
    const t = tables || {};
    const parts = [
        buildSection(lang('2. Mauzo ya Wateja wa Mkopo/Credit', '2. Credit/Debt Customer Sales'), t.sales && t.sales.length ? buildSalesTable(t.sales) : `<p class="daily-empty-note mb-0">${lang('Hakuna mauzo ya wateja wa mkopo/credit', 'No credit/debt customer sales')}</p>`, 'daily-section-sales'),
        buildSection(lang('3. Malipo ya Madeni — Wateja', '3. Customer Debt Payments'), t.customer_pays && t.customer_pays.length ? buildCustomerPayTable(t.customer_pays) : `<p class="daily-empty-note mb-0">${lang('Hakuna malipo ya madeni', 'No debt payments')}</p>`, 'daily-section-payments'),
        buildSection(lang('4. Malipo ya Simu', '4. Mobile Payments'), t.mobile_pays && t.mobile_pays.length ? buildMobilePayTable(t.mobile_pays) : `<p class="daily-empty-note mb-0">${lang('Hakuna malipo ya simu', 'No mobile payments')}</p>`, 'daily-section-payments'),
        buildSection(lang('5. Kuweka Benki / Toa Pesa', '5. Cash Deposits'), t.cash_deposits && t.cash_deposits.length ? buildCashDepTable(t.cash_deposits) : `<p class="daily-empty-note mb-0">${lang('Hakuna amana za pesa', 'No cash deposits')}</p>`, 'daily-section-payments'),
        buildSection(lang('6. Kuhamisha Mafuta', '6. Fuel Transfers'), t.transfers && t.transfers.length ? buildTransferTable(t.transfers) : `<p class="daily-empty-note mb-0">${lang('Hakuna transfer', 'No transfers')}</p>`, 'daily-section-fuel'),
        buildSection(lang('7. Kupokea Mafuta', '7. Fuel Receives'), t.receives && t.receives.length ? buildReceiveTable(t.receives) : `<p class="daily-empty-note mb-0">${lang('Hakuna receive', 'No receives')}</p>`, 'daily-section-fuel'),
        buildSection(lang('8. Matumizi', '8. Expenses'), t.expenses && t.expenses.length ? buildExpenseTable(t.expenses) : `<p class="daily-empty-note mb-0">${lang('Hakuna matumizi', 'No expenses')}</p>`, 'daily-section-exp'),
    ];
    return parts.join('');
};

const renderDayDetail = data => {
    activeDayDetail = data;
    const dateLabel = moment(data.date).format('DD/MM/YYYY');
    $('#dayDetailTitle').html(`${lang('Maelezo ya Siku', 'Day Details')} — <span class="bluePrint">${dateLabel}</span>${data.stN ? ` · ${escapeDailyHtml(data.stN)}` : ''}`);

    const header = `
      <div class="daily-day-header">
        <div class="daily-day-header-grid">
          <div class="daily-day-header-item"><strong>${lang('Tarehe', 'Date')}:</strong> ${dateLabel}</div>
          <div class="daily-day-header-item"><strong>${lang('Kituo', 'Station')}:</strong> ${escapeDailyHtml(data.stN || lang('Vituo Vyote', 'All Stations'))}</div>
          <div class="daily-day-header-item"><strong>${lang('Sessions', 'Sessions')}:</strong> ${(data.summary || {}).session_count || 0} · <strong>${lang('Zamu', 'Shifts')}:</strong> ${(data.summary || {}).shift_count || 0}</div>
        </div>
      </div>`;

    const html = header
        + buildShiftsSection(data.sessions)
        + buildActivityTablesSection(data.tables)
        + buildEvaluationSections(data.evaluations);

    $('#dayDetailContent').html(html);
    $('#paymentDetails').hide();
    $('#paymentDayDetail').show();
};

const loadDayDetail = (date, st, stN) => {
    $('#loadMe').modal('show');
    POSTREQUEST({ data: { date, st }, url: dayDetailEndpoint }).then(res => {
        $('#loadMe').modal('hide');
        hideLoading();
        if (res.success) {
            if (stN && !res.stN) res.stN = stN;
            renderDayDetail(res);
        } else {
            toastr.error(lang(res.swa, res.eng), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
        }
    }).catch(() => {
        $('#loadMe').modal('hide');
        hideLoading();
        toastr.error(lang('Tatizo la mtandao', 'Network error'), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
    });
};

$('body').on('click', '.day-detail-row', function (e) {
    if ($(e.target).closest('a').length) return;
    const date = $(this).data('date');
    const st = Number($(this).data('st') || 0);
    const stN = $(this).data('stn') || '';
    loadDayDetail(date, st, stN);
});

const prepareDayDetailPrintContent = (html, includeAttach) => {
    const $root = $('<div>').html(html);

    if (!includeAttach) {
        $root.find('.daily-shift-attachments').remove();
    }

    $root.find('.daily-session-group').each(function () {
        if (!$(this).find('.daily-shift-card').length) {
            $(this).remove();
        }
    });

    $root.find('.daily-section').each(function () {
        const $sec = $(this);
        const hasDataRows = $sec.find('.daily-mini-table tbody tr').length > 0;
        const hasShiftCards = $sec.find('.daily-shift-card').length > 0;

        if ($sec.find('.daily-empty-note').length && !hasDataRows && !hasShiftCards) {
            $sec.remove();
            return;
        }

        if ($sec.hasClass('daily-section-shifts') && !hasShiftCards) {
            $sec.remove();
            return;
        }

        if ($sec.hasClass('daily-section-pump-pay')) {
            const p = (activeDayDetail && activeDayDetail.evaluations && activeDayDetail.evaluations.pump_payments) || {};
            const hasPumpData = ['tot_psa', 'tot_exp', 'tot_cab', 'tot_req', 'tot_paid'].some(
                k => Math.abs(Number(p[k] || 0)) > 0.000001,
            );
            if (!hasPumpData) {
                $sec.remove();
            }
        }
    });

    return $root.html();
};

const getDailyPrintHeaderHtml = () => {
    const $hdr = $('#CompanyTitle');
    if (!$hdr.length) return '';
    return `<div class="daily-print-header">${$hdr.html()}</div>`;
};

const getDayDetailPrintStyles = () => `
  <style>
    @page { size: A4 portrait; margin: 10mm 8mm; }
    *, *::before, *::after { box-sizing: border-box; }
    html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 10px;
      font-weight: 600;
      color: #000;
      overflow: visible;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .daily-print-wrap { width: 100%; max-width: 100%; padding: 0; }
    .daily-print-title {
      font-size: 14px;
      margin: 0 0 8px;
      font-weight: 800;
      color: #0056b3 !important;
      border-left: 4px solid #0056b3;
      padding-left: 8px;
    }
    .daily-print-header { margin-bottom: 8px; page-break-after: avoid; break-after: avoid; }
    .daily-print-header .header-main-title {
      color: #0056b3 !important;
      font-size: 16px;
      font-weight: 800;
      letter-spacing: 0.5px;
      margin: 0 0 4px;
      text-align: center;
      text-transform: uppercase;
    }
    .daily-print-header .header-details { display: flex; justify-content: center; align-items: center; gap: 16px; padding: 2px 0; width: 100%; }
    .daily-print-header .contact-info,
    .daily-print-header .address-info {
      font-size: 9px;
      line-height: 1.35;
      font-weight: 700;
      color: #000 !important;
    }
    .daily-print-header .contact-info { text-align: right; }
    .daily-print-header .address-info { text-align: left; }
    .daily-print-header .logo-container img { width: 44px; height: auto; display: block; margin: 0 auto; }
    .daily-print-header .blue-line { height: 3px; background: #0056b3 !important; margin: 4px 0 0; width: 100%; }
    .daily-print-header p { margin: 0 0 2px; color: #000 !important; font-weight: 600; }
    .daily-day-header {
      border: 1px solid #0056b3 !important;
      padding: 6px 8px;
      margin-bottom: 8px;
      background: #e8f4fd !important;
      page-break-after: avoid;
    }
    .daily-day-header-table td { width: 33.33%; font-weight: 700; color: #000 !important; }
    .daily-section {
      page-break-inside: auto;
      break-inside: auto;
      margin-bottom: 8px;
      border: 1px solid #000 !important;
      background: #fff !important;
      overflow: hidden;
    }
    .daily-section-body { padding: 5px 6px; color: #000 !important; }
    .daily-section-title {
      padding: 6px 10px;
      font-size: 11px;
      font-weight: 800 !important;
      color: #fff !important;
      background: #0056b3 !important;
      border-bottom: none !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .daily-section-shifts .daily-section-title { background: #0d6efd !important; }
    .daily-section-sales .daily-section-title { background: #198754 !important; }
    .daily-section-payments .daily-section-title { background: #6f42c1 !important; }
    .daily-section-fuel .daily-section-title { background: #e8590c !important; }
    .daily-section-exp .daily-section-title { background: #dc3545 !important; }
    .daily-section-eval .daily-section-title { background: #087990 !important; }
    .daily-eval-wide-table { min-width: 100%; font-size: 8.5px; font-weight: 600; }
    .daily-print-wrap table {
      width: 100%;
      max-width: 100%;
      border-collapse: collapse !important;
      border: 1px solid #000 !important;
    }
    .daily-print-wrap table th,
    .daily-print-wrap table td {
      border: 1px solid #000 !important;
      color: #000 !important;
      font-weight: 600;
    }
    .daily-mini-table {
      width: 100%;
      max-width: 100%;
      border-collapse: collapse !important;
      font-size: 9px;
      font-weight: 600;
      table-layout: fixed;
      border: 1px solid #000 !important;
    }
    .daily-mini-table th,
    .daily-mini-table td {
      border: 1px solid #000 !important;
      padding: 3px 5px;
      text-align: left;
      vertical-align: top;
      word-wrap: break-word;
      overflow-wrap: anywhere;
      color: #000 !important;
      font-weight: 600;
    }
    .daily-mini-table thead th {
      background: #dbeafe !important;
      color: #1e3a8a !important;
      font-weight: 800 !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .daily-mini-table tfoot td {
      background: #f1f5f9 !important;
      color: #000 !important;
      font-weight: 800 !important;
      border-top: 2px solid #000 !important;
    }
    .daily-mini-table tbody tr:nth-child(even) td {
      background: #f8fafc !important;
    }
    .daily-pump-table thead th {
      background: #dbeafe !important;
      color: #1e40af !important;
      font-weight: 800 !important;
    }
    .daily-shift-summary-table thead th {
      background: #e0e7ff !important;
      color: #3730a3 !important;
      font-weight: 800 !important;
    }
    .daily-mini-table tr.daily-summary-grey th,
    .daily-mini-table tr.daily-summary-grey td {
      background: #e2e8f0 !important;
      color: #000 !important;
      font-weight: 800 !important;
      border: 1px solid #000 !important;
    }
    .daily-mini-table tr.daily-summary-green th,
    .daily-mini-table tr.daily-summary-green td {
      background: #bbf7d0 !important;
      color: #14532d !important;
      font-weight: 800 !important;
      border: 1px solid #000 !important;
    }
    .daily-mini-table tr.daily-summary-loss th,
    .daily-mini-table tr.daily-summary-loss td {
      background: #fecaca !important;
      color: #7f1d1d !important;
      font-weight: 800 !important;
      border: 1px solid #000 !important;
    }
    .daily-shift-meta-table td { width: 50%; font-weight: 600; background: #f8fafc !important; }
    .daily-sign-table td { width: 50%; min-height: 36px; font-weight: 600; }
    .daily-shift-card {
      page-break-inside: avoid;
      break-inside: avoid;
      border: 1px solid #64748b !important;
      padding: 5px;
      margin-bottom: 5px;
      background: #fff !important;
    }
    .daily-session-group {
      page-break-inside: auto;
      break-inside: auto;
      border: 1px solid #93c5fd !important;
      padding: 5px;
      margin-bottom: 5px;
      background: #f8fbff !important;
    }
    .daily-session-head {
      font-size: 9px;
      font-weight: 800;
      margin-bottom: 4px;
      padding: 4px 6px;
      border-bottom: none !important;
      color: #1e40af !important;
      background: #dbeafe !important;
    }
    .daily-pump-title {
      font-weight: 800;
      margin: 4px 0 2px;
      color: #92400e !important;
      font-size: 9.5px;
      background: #fef3c7;
      padding: 2px 6px;
      border-left: 3px solid #f59e0b;
    }
    .daily-pump-title u { text-decoration: underline; }
    .daily-print-wrap a,
    .daily-print-wrap a:visited {
      color: #0056b3 !important;
      text-decoration: underline;
      font-weight: 700;
    }
    .daily-print-wrap .text-danger { color: #991b1b !important; font-weight: 800 !important; }
    .daily-print-wrap .text-success { color: #166534 !important; font-weight: 800 !important; }
    .daily-empty-note { color: #475569 !important; font-style: italic; font-weight: 600; padding: 4px 0; }
    .analog-shift-card { border-left: 4px solid #f59e0b !important; background: #fffbeb !important; }
    .analog-pump-row td {
      background: #fef3c7 !important;
      color: #000 !important;
      font-weight: 700 !important;
    }
    .daily-analog-tag {
      display: inline-block;
      font-size: 7px;
      font-weight: 800;
      line-height: 1.2;
      color: #000 !important;
      background: #fcd34d !important;
      border: 1px solid #b45309;
      border-radius: 2px;
      padding: 1px 5px;
      margin-left: 4px;
      white-space: nowrap;
      vertical-align: middle;
    }
    .daily-analog-tag-sm { font-size: 7px; padding: 1px 4px; }
    .daily-analog-tag-shift { font-size: 8px; margin-left: 6px; }
    .daily-shift-attachments { border-top: 1px dashed #94a3b8; padding-top: 6px; }
    .daily-attach-heading { font-size: 9px; font-weight: 800; color: #334155 !important; margin-bottom: 4px; }
    .daily-attach-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
    .daily-attach-card {
      display: block;
      border: 1px solid #64748b !important;
      border-radius: 0;
      overflow: hidden;
      text-decoration: none !important;
      color: #000 !important;
      background: #fff;
      page-break-inside: avoid;
      break-inside: avoid;
    }
    .daily-attach-thumb { width: 100%; height: 72px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; overflow: hidden; border-bottom: 1px solid #000; }
    .daily-attach-img { width: 100%; height: 72px; object-fit: cover; display: block; }
    .daily-attach-file-fallback { font-size: 8px; font-weight: 800; color: #000 !important; }
    .daily-attach-meta { padding: 3px 4px; border-top: 1px solid #cbd5e1; background: #f8fafc; }
    .daily-attach-name { font-size: 7.5px; font-weight: 800; line-height: 1.2; color: #000 !important; }
    .daily-attach-sub { font-size: 7px; color: #475569 !important; font-weight: 600; line-height: 1.2; }
    .daily-pump-pay-table { max-width: 100%; border: 1px solid #000 !important; }
    .badge { display: none !important; }
  </style>`;

$('#printDayDetail').on('click', function () {
    if (!activeDayDetail) return;
    const includeAttach = $('#printIncludeAttachments').prop('checked');
    let content = prepareDayDetailPrintContent(
        document.getElementById('dayDetailContent').innerHTML,
        includeAttach,
    );
    const title = $('#dayDetailTitle').text();
    const fullHtml = '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Daily Sales</title>'
        + getDayDetailPrintStyles()
        + '</head><body><div class="daily-print-wrap">'
        + getDailyPrintHeaderHtml()
        + `<h2 class="daily-print-title">${escapeDailyHtml(title)}</h2>`
        + `<div class="daily-print-content">${content}</div>`
        + '</div></body></html>';
    openAndPrintDocument(fullHtml, { fullDocument: true });
});

$('#stationFilter').on('change', function () {
    renderSummary();
    if ($('#paymentDayDetail').is(':visible')) {
        $('#backToDayList').click();
    }
    if ($('#paymentDetails').is(':visible') && activeDetail) {
        renderDetails(activeDetail);
    }
});

$('#customDateSubmit').on('click', function () {
    const tFr = moment($('#startDate').val()).format();
    const tTo = moment($('#endDate').val()).format();
    const rname = $('#durationName').val();

    if (!rname) {
        redborder('#durationName');
        toastr.error(lang('Tafadhali weka jina la muda', 'Please enter duration name'), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
        return;
    }

    if (!tFr || !tTo) {
        toastr.error(lang('Tafadhali chagua tarehe zote mbili', 'Please select both dates'), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
        return;
    }

    $('#durationModal').modal('hide');
    createArray(rname, tFr, tTo);
});

$('#printPayments').on('click', function () {
    if (!activeDetail) {
        toastr.error(lang('Hakuna data ya kuchapisha', 'No data to print'), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
        return;
    }

    const { st } = filters();
    const stationName = st ? ($('#stationFilter').find('option:selected').data('stxn') || '') : lang('Vituo Vyote', 'All Stations');
    const userN = ($('#user_userName').val() || '').trim();
    const tFr = activeDetail.tFr;
    const tTo = activeDetail.tTo;
    const ddiff = moment(tTo).diff(moment(tFr), 'days');
    const reportDuration = ddiff > 1
        ? `${moment(tFr).format('DD/MM/YYYY')} - ${moment(tTo).format('DD/MM/YYYY')}`
        : moment(tTo).format('DD/MM/YYYY');

    const heading = `<h2>${lang('Mauzo Kilasiku', 'Daily Sales')}: ${reportDuration}</h2>`;
    const statementDetails = `<div class="row my-3">
        <div class="col-6 row">
            <div class="col-5">${lang('Kituo', 'Station')}:</div>
            <div class="col-7">${stationName}</div>
            <div class="col-5">${lang('Imetolewa', 'Issued on')}:</div>
            <div class="col-7">${moment().format('DD/MM/YYYY HH:mm')}</div>
            <div class="col-5">${lang('Imetolewa na', 'Issued by')}:</div>
            <div class="col-7 text-capitalize">${userN}</div>
        </div>
    </div>`;

    const theReportData = document.getElementById('paymentsTable').innerHTML;
    openAndPrintDocument(`${heading}${statementDetails}${theReportData}`);
});
