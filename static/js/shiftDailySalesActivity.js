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
        mobile_amount: 0,
        customer_pay_amount: 0,
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
        totals.mobile_amount += Number(d.mobile_amount || 0);
        totals.customer_pay_amount += Number(d.customer_pay_amount || 0);
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

const amountCell = (amount, count) => {
    const amt = formatNumber(amount || 0);
    if (!count) return `<span class="text-muted">—</span>`;
    return `${amt}<span class="sub-label">${count} ${lang('rekodi', 'records')}</span>`;
};

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
            <td>${formatNumber(t.sales_amount)}</td>
            <td>${formatNumber(t.mobile_amount)}</td>
            <td>${formatNumber(t.customer_pay_amount)}</td>
            <td>${formatNumber(t.dep_before_amount)}</td>
            <td>${formatNumber(t.cash_dep_amount)}</td>
            <td>${formatNumber(t.expenses_amount)}</td>
            <td>${formatNumber(t.transfer_qty)} L<br><span class="sub-label">${formatNumber(t.transfer_worth)}</span></td>
            <td>${formatNumber(t.receive_qty)} L<br><span class="sub-label">${formatNumber(t.receive_worth)}</span></td>
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
            <td>${amountCell(r.sales_amount, r.sales_count)}</td>
            <td>${amountCell(r.mobile_amount, r.mobile_count)}</td>
            <td>${amountCell(r.customer_pay_amount, r.customer_pay_count)}</td>
            <td>${amountCell(r.dep_before_amount, r.dep_before_count)}</td>
            <td>${amountCell(r.cash_dep_amount, r.cash_dep_count)}</td>
            <td>${amountCell(r.expenses_amount, r.expenses_count)}</td>
            <td>${qtyWorthCell(r.transfer_qty, r.transfer_worth, r.transfer_count)}</td>
            <td>${qtyWorthCell(r.receive_qty, r.receive_worth, r.receive_count)}</td>
        </tr>`;
    });

    const t = sumDays(rows);
    tr += `<tr class="smallFont font-weight-bold">
        <td colspan="3">${lang('Jumla', 'Total')}</td>
        <td>${formatNumber(t.sales_amount)}</td>
        <td>${formatNumber(t.mobile_amount)}</td>
        <td>${formatNumber(t.customer_pay_amount)}</td>
        <td>${formatNumber(t.dep_before_amount)}</td>
        <td>${formatNumber(t.cash_dep_amount)}</td>
        <td>${formatNumber(t.expenses_amount)}</td>
        <td>${formatNumber(t.transfer_qty)} L / ${formatNumber(t.transfer_worth)}</td>
        <td>${formatNumber(t.receive_qty)} L / ${formatNumber(t.receive_worth)}</td>
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
    return `<table class="daily-mini-table"><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead><tbody>${body}</tbody>${foot}</table>`;
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
      <table class="daily-mini-table daily-pump-table mb-2">
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
      </table>`;
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
    headers: ['#', lang('Session', 'Session'), lang('Ankara', 'Invoice'), lang('Mteja', 'Customer'), lang('Mafuta', 'Fuel'), lang('Kiasi L', 'Qty L'), lang('Thamani', 'Amount'), lang('Mhusika', 'Attendant')],
    rows: (rows || []).map((r, i) => [
        i + 1,
        escapeDailyHtml(r.session_name || '—'),
        r.sale_id ? `<a href="/salepurchase/viewFuelSales?i=${r.sale_id}">${escapeDailyHtml(r.sale_code || '')}</a>` : escapeDailyHtml(r.sale_code || '—'),
        escapeDailyHtml(r.cust_name || '—'),
        escapeDailyHtml(r.fuel_name || ''),
        formatNumber(r.qty_sold),
        formatNumber(r.amount),
        escapeDailyHtml(r.attendant || '—'),
    ]),
    footer: [lang('Jumla', 'Total'), '', '', '', '', formatNumber(sumField(rows, 'qty_sold')), formatNumber(sumField(rows, 'amount')), ''],
});

const buildCustomerPayTable = rows => buildMiniTable({
    headers: ['#', lang('Session', 'Session'), lang('Tarehe', 'Date'), lang('Mteja', 'Customer'), lang('Akaunti', 'Account'), lang('Mhusika', 'Attendant'), lang('Kiasi', 'Amount')],
    rows: (rows || []).map((r, i) => [i + 1, escapeDailyHtml(r.session_name || ''), fmtDt(r.tarehe), escapeDailyHtml(r.cust_name || '—'), escapeDailyHtml(r.account_name || ''), escapeDailyHtml(r.attendant || '—'), formatNumber(r.Amount)]),
    footer: [lang('Jumla', 'Total'), '', '', '', '', '', formatNumber(sumField(rows, 'Amount'))],
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

const buildAdjustmentTable = rows => buildMiniTable({
    headers: ['#', lang('Session', 'Session'), lang('Noti', 'Note'), lang('Tanki', 'Tank'), lang('Mafuta', 'Fuel'), lang('Kabla L', 'Opening L'), lang('Stick L', 'Stick L'), lang('Tofauti L', 'Diff L'), lang('Thamani', 'Worth')],
    rows: (rows || []).map((r, i) => [
        i + 1, escapeDailyHtml(r.session_name || ''),
        r.adj_id ? `<a href="/salepurchase/adjView?i=${r.adj_id}">ADJ-${escapeDailyHtml(r.adj_code || '')}</a>` : '—',
        escapeDailyHtml(r.tank_name || ''), escapeDailyHtml(r.fuel_name || ''),
        formatNumber(r.read), formatNumber(r.stick), formatNumber(r.diff), formatNumber(r.worth),
    ]),
    footer: [lang('Jumla', 'Total'), '', '', '', '', '', '', formatNumber(sumField(rows, 'diff')), formatNumber(sumField(rows, 'worth'))],
});

const buildExpenseTable = rows => buildMiniTable({
    headers: ['#', lang('Session', 'Session'), lang('Aina', 'Type'), lang('Tarehe', 'Date'), lang('Mhusika', 'Attendant'), lang('Kiasi', 'Amount'), lang('Mafuta L', 'Fuel L')],
    rows: (rows || []).map((r, i) => [i + 1, escapeDailyHtml(r.session_name || ''), escapeDailyHtml(r.exp_name || ''), fmtDt(r.tarehe), escapeDailyHtml(r.attendant || '—'), formatNumber(r.kiasi), formatNumber(r.fuel_qty)]),
    footer: [lang('Jumla', 'Total'), '', '', '', '', formatNumber(sumField(rows, 'kiasi')), formatNumber(sumField(rows, 'fuel_qty'))],
});

const buildActivityTablesSection = tables => {
    const t = tables || {};
    const parts = [
        buildSection(lang('2. Mauzo kwa Wateja Muhimu', '2. Key Customer Sales'), t.sales && t.sales.length ? buildSalesTable(t.sales) : `<p class="daily-empty-note mb-0">${lang('Hakuna mauzo', 'No sales')}</p>`, 'daily-section-sales'),
        buildSection(lang('3. Malipo ya Madeni — Wateja', '3. Customer Debt Payments'), t.customer_pays && t.customer_pays.length ? buildCustomerPayTable(t.customer_pays) : `<p class="daily-empty-note mb-0">${lang('Hakuna malipo ya madeni', 'No debt payments')}</p>`, 'daily-section-payments'),
        buildSection(lang('4. Malipo ya Simu', '4. Mobile Payments'), t.mobile_pays && t.mobile_pays.length ? buildMobilePayTable(t.mobile_pays) : `<p class="daily-empty-note mb-0">${lang('Hakuna malipo ya simu', 'No mobile payments')}</p>`, 'daily-section-payments'),
        buildSection(lang('5. Kuweka Benki / Toa Pesa', '5. Cash Deposits'), t.cash_deposits && t.cash_deposits.length ? buildCashDepTable(t.cash_deposits) : `<p class="daily-empty-note mb-0">${lang('Hakuna amana za pesa', 'No cash deposits')}</p>`, 'daily-section-payments'),
        buildSection(lang('6. Kuhamisha Mafuta', '6. Fuel Transfers'), t.transfers && t.transfers.length ? buildTransferTable(t.transfers) : `<p class="daily-empty-note mb-0">${lang('Hakuna transfer', 'No transfers')}</p>`, 'daily-section-fuel'),
        buildSection(lang('7. Kupokea Mafuta', '7. Fuel Receives'), t.receives && t.receives.length ? buildReceiveTable(t.receives) : `<p class="daily-empty-note mb-0">${lang('Hakuna receive', 'No receives')}</p>`, 'daily-section-fuel'),
        buildSection(lang('8. Marekebisho / Vipimo vya Matanki', '8. Tank Adjustments'), t.adjustments && t.adjustments.length ? buildAdjustmentTable(t.adjustments) : `<p class="daily-empty-note mb-0">${lang('Hakuna marekebisho', 'No adjustments')}</p>`, 'daily-section-adj'),
        buildSection(lang('9. Matumizi', '9. Expenses'), t.expenses && t.expenses.length ? buildExpenseTable(t.expenses) : `<p class="daily-empty-note mb-0">${lang('Hakuna matumizi', 'No expenses')}</p>`, 'daily-section-exp'),
    ];
    return parts.join('');
};

const buildDaySummarySection = summary => {
    const s = summary || {};
    const rows = [
        [lang('Sessions', 'Sessions'), s.session_count, lang('Zamu', 'Shifts'), s.shift_count],
        [lang('Mauzo', 'Sales'), `${formatNumber(s.sales_amount)} (${s.sales_count || 0})`, lang('Malipo Wateja', 'Cust. Pay'), formatNumber(s.customer_pay_amount)],
        [lang('Malipo Simu', 'Mobile Pay'), formatNumber(s.mobile_amount), lang('Benki/Toa Pesa', 'Cash Dep.'), formatNumber(s.cash_dep_amount)],
        [lang('Transfer L', 'Transfer L'), formatNumber(s.transfer_qty), lang('Transfer', 'Transfer'), formatNumber(s.transfer_worth)],
        [lang('Receive L', 'Receive L'), formatNumber(s.receive_qty), lang('Receive', 'Receive'), formatNumber(s.receive_worth)],
        [lang('Marekebisho L', 'Adj. Diff L'), formatNumber(s.adjustment_diff), lang('Matumizi', 'Expenses'), formatNumber(s.expense_amount)],
    ];
    const table = `
      <table class="daily-mini-table daily-summary-table">
        <thead><tr><th>${lang('Kipimo', 'Metric')}</th><th>${lang('Thamani', 'Value')}</th><th>${lang('Kipimo', 'Metric')}</th><th>${lang('Thamani', 'Value')}</th></tr></thead>
        <tbody>${rows.map(r => `<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join('')}</tbody>
      </table>`;
    return buildSection(lang('10. Muhtasari wa Siku', '10. Day Summary'), table, 'daily-section-summary');
};

const renderDayDetail = data => {
    activeDayDetail = data;
    const dateLabel = moment(data.date).format('DD/MM/YYYY');
    $('#dayDetailTitle').html(`${lang('Maelezo ya Siku', 'Day Details')} — <span class="bluePrint">${dateLabel}</span>${data.stN ? ` · ${escapeDailyHtml(data.stN)}` : ''}`);

    const header = `
      <div class="daily-day-header">
        <table class="daily-mini-table daily-day-header-table mb-0">
          <tbody>
            <tr>
              <td><strong>${lang('Tarehe', 'Date')}:</strong> ${dateLabel}</td>
              <td><strong>${lang('Kituo', 'Station')}:</strong> ${escapeDailyHtml(data.stN || lang('Vituo Vyote', 'All Stations'))}</td>
              <td><strong>${lang('Sessions', 'Sessions')}:</strong> ${(data.summary || {}).session_count || 0} · <strong>${lang('Zamu', 'Shifts')}:</strong> ${(data.summary || {}).shift_count || 0}</td>
            </tr>
          </tbody>
        </table>
      </div>`;

    const html = header
        + buildShiftsSection(data.sessions)
        + buildActivityTablesSection(data.tables)
        + buildDaySummarySection(data.summary);

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
      font-family: Arial, sans-serif;
      font-size: 9px;
      color: #000;
      overflow: visible;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .daily-print-wrap { width: 100%; max-width: 100%; padding: 0; }
    .daily-print-title { font-size: 13px; margin: 0 0 6px; font-weight: 700; }
    .daily-print-header { margin-bottom: 6px; page-break-after: avoid; break-after: avoid; }
    .daily-print-header .header-main-title { color: #007bff; font-size: 15px; font-weight: 700; letter-spacing: 1px; margin: 0 0 4px; text-align: center; text-transform: uppercase; }
    .daily-print-header .header-details { display: flex; justify-content: center; align-items: center; gap: 16px; padding: 2px 0; width: 100%; }
    .daily-print-header .contact-info, .daily-print-header .address-info { font-size: 8px; line-height: 1.3; font-weight: 600; color: #000; }
    .daily-print-header .contact-info { text-align: right; }
    .daily-print-header .address-info { text-align: left; }
    .daily-print-header .logo-container img { width: 44px; height: auto; display: block; margin: 0 auto; }
    .daily-print-header .blue-line { height: 2px; background: #007bff; margin: 4px 0 0; width: 100%; }
    .daily-print-header p { margin: 0 0 2px; }
    .page { margin: 0 !important; page-break-after: avoid !important; box-shadow: none !important; width: 100% !important; overflow: visible !important; }
    .daily-section { page-break-inside: auto; break-inside: auto; margin-bottom: 6px; border: 1px solid #ccc; }
    .daily-section-body { padding: 4px 6px; }
    .daily-section-title { padding: 4px 8px; font-size: 10px; font-weight: 700; color: #fff !important; background: #006ae4 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .daily-section-shifts .daily-section-title { background: #0d6efd !important; }
    .daily-section-sales .daily-section-title { background: #198754 !important; }
    .daily-section-payments .daily-section-title { background: #6f42c1 !important; }
    .daily-section-fuel .daily-section-title { background: #fd7e14 !important; }
    .daily-section-adj .daily-section-title { background: #20c997 !important; }
    .daily-section-exp .daily-section-title { background: #dc3545 !important; }
    .daily-section-summary .daily-section-title { background: #343a40 !important; }
    .daily-mini-table { width: 100%; max-width: 100%; border-collapse: collapse; font-size: 8px; table-layout: fixed; }
    .daily-mini-table th, .daily-mini-table td { border: 1px solid #bbb; padding: 2px 4px; text-align: left; vertical-align: top; word-wrap: break-word; overflow-wrap: anywhere; color: #000 !important; }
    .daily-mini-table thead th { background: #e9ecef !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; font-weight: 700; }
    .daily-mini-table tfoot td { background: #f1f3f5 !important; font-weight: 700; }
    .daily-pump-table thead th { background: #e7f1ff !important; color: #084298 !important; }
    .daily-shift-meta-table td { width: 50%; }
    .daily-sign-table td { width: 50%; height: 36px; }
    .daily-day-header-table td { width: 33.33%; }
    .daily-shift-card { page-break-inside: avoid; break-inside: avoid; border: 1px solid #ddd; padding: 4px; margin-bottom: 4px; }
    .daily-session-group { page-break-inside: auto; break-inside: auto; border: 1px solid #cfe2ff; padding: 4px; margin-bottom: 4px; }
    .daily-session-head { font-size: 8px; font-weight: 700; margin-bottom: 4px; padding-bottom: 3px; border-bottom: 1px dashed #b6d4fe; color: #084298 !important; }
    .daily-pump-title { font-weight: 700; margin: 4px 0 2px; color: #000 !important; }
    .daily-pump-title u { text-decoration: underline; }
    .daily-day-header { border: 1px solid #b8daff; padding: 4px; margin-bottom: 6px; background: #f0f7ff !important; page-break-after: avoid; }
    .daily-empty-note { color: #444 !important; font-style: italic; padding: 4px 0; }
    .analog-shift-card { border-left: 3px solid #856404 !important; }
    .analog-pump-row td { background: #fff3cd !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .daily-analog-tag {
      display: inline-block;
      font-size: 7px;
      font-weight: 700;
      line-height: 1.2;
      color: #000 !important;
      background: #ffc107 !important;
      border: 1px solid #856404;
      border-radius: 2px;
      padding: 1px 5px;
      margin-left: 4px;
      white-space: nowrap;
      vertical-align: middle;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .daily-analog-tag-sm { font-size: 6.5px; padding: 1px 4px; }
    .daily-analog-tag-shift { font-size: 7.5px; margin-left: 6px; }
    .daily-pump-title .daily-analog-tag { margin-left: 6px; vertical-align: baseline; }
    .daily-shift-attachments { border-top: 1px dashed #dee2e6; padding-top: 6px; }
    .daily-attach-heading { font-size: 9px; font-weight: 700; color: #495057; margin-bottom: 4px; }
    .daily-attach-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
    .daily-attach-card { display: block; border: 1px solid #ced4da; border-radius: 4px; overflow: hidden; text-decoration: none !important; color: #000 !important; background: #fff; page-break-inside: avoid; break-inside: avoid; }
    .daily-attach-thumb { width: 100%; height: 72px; background: #f8f9fa; display: flex; align-items: center; justify-content: center; overflow: hidden; }
    .daily-attach-img { width: 100%; height: 72px; object-fit: cover; display: block; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .daily-attach-file-fallback { font-size: 8px; font-weight: 700; color: #6c757d; }
    .daily-attach-meta { padding: 3px 4px; border-top: 1px solid #eee; }
    .daily-attach-name { font-size: 7px; font-weight: 700; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .daily-attach-sub { font-size: 6.5px; color: #666; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    a { color: #000 !important; text-decoration: none; }
    .badge { display: none !important; }
  </style>`;

$('#printDayDetail').on('click', function () {
    if (!activeDayDetail) return;
    const includeAttach = $('#printIncludeAttachments').prop('checked');
    let content = document.getElementById('dayDetailContent').innerHTML;
    if (!includeAttach) {
        const $tmp = $('<div>').html(content);
        $tmp.find('.daily-shift-attachments').remove();
        content = $tmp.html();
    }
    const title = $('#dayDetailTitle').text();
    const printWindow = window.open('', '', 'height=800,width=1100');
    printWindow.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Daily Sales</title>');
    printWindow.document.write(getDayDetailPrintStyles());
    printWindow.document.write('</head><body><div class="daily-print-wrap">');
    printWindow.document.write(getDailyPrintHeaderHtml());
    printWindow.document.write(`<h2 class="daily-print-title">${escapeDailyHtml(title)}</h2>`);
    printWindow.document.write(`<div class="daily-print-content">${content}</div>`);
    printWindow.document.write('</div></body></html>');
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => printWindow.print(), 600);
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
    const printWindow = window.open('', '', 'height=600,width=1200');
    printWindow.document.write(company_header);
    printWindow.document.write(`${heading}${statementDetails}${theReportData}`);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();
});
