let psPayData = [];
let psActiveRowId = null;

const psFilters = () => {
    const st = Number($('#stationFilter').val()) || 0;
    const today = {
        key: 'today',
        rname: lang('Leo', 'Today'),
        tFr: moment().startOf('day').format(),
        tTo: moment().format(),
    };
    const week = {
        key: 'week',
        rname: lang('Wiki Hii', 'This Week'),
        tFr: moment().startOf('isoWeek').format(),
        tTo: moment().format(),
    };
    const month = {
        key: 'month',
        rname: lang('Mwezi Huu', 'This Month'),
        tFr: moment().startOf('month').format(),
        tTo: moment().format(),
    };
    return {
        st,
        today,
        week,
        month,
        account: Number($('#psAccountFilter').val()) || 0,
        recordedBy: Number($('#psRecordedByFilter').val()) || 0,
        paymentType: $('#psTypeFilter').val() || '',
        direction: $('#psDirectionFilter').val() || '',
    };
};

const psTypeLabel = (type) => {
    const map = {
        mobile_payment: lang('Malipo kwa Simu', 'Mobile Payment'),
        customer_payment: lang('Malipo ya Wateja', 'Customer Payment'),
        cash_deposit: lang('Kuweka Kabla ya Zamu', 'Cash Deposit Before Shift'),
        pump_attendant: lang('Malipo ya Pump Attendant', 'Pump Attendant Payment'),
        bank_deposit: lang('Kuweka Benki', 'Bank Deposit'),
        expense: lang('Matumizi', 'Expense'),
        bill_payment: lang('Malipo ya Bili', 'Bill Payment'),
        personal: lang('Binafsi', 'Personal'),
        other_receive: lang('Mengine (Mapokezi)', 'Other Receive'),
        other_payment: lang('Mengine (Malipo)', 'Other Payment'),
    };
    return map[type] || type || '-';
};

const psFormatNumber = (value) => Number(value || 0).toLocaleString();

const psAmountCell = (value, className = '') => {
    if (value === null || value === undefined) {
        return `<td class="text-right text-muted">---</td>`;
    }
    return `<td class="text-right ${className}">${psFormatNumber(value)}</td>`;
};

const psTitleCase = (text) => {
    if (!text) return '';
    return String(text).replace(/\w\S*/g, (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());
};

const psRenderFromCell = (item) => {
    const parts = [];
    if (item.mauzo || item.shift_id) {
        parts.push(lang('Mauzo', 'Sales'));
    }
    if (item.cd_order_id) {
        parts.push(lang('Malipo ya Order', 'Order Payment'));
    }
    if (item.kuhamisha && item.kutoka) {
        parts.push(item.kutoka);
    }
    if (!item.huduma && !item.mauzo && !item.kuhamisha && !item.bifore_shift && !item.cd_order_id) {
        parts.push(lang('Mtaji', 'Capital'));
    }
    if (!parts.length) {
        return '<span class="text-muted">---</span>';
    }
    return `<u class="bluePrint px-2">${parts.join(' ')}</u>`;
};

const psRenderToCell = (item) => {
    const parts = [];
    if (item.expense_name) {
        parts.push(psTitleCase(item.expense_name));
    }
    if (item.kuhamisha && item.kwenda) {
        parts.push(item.kwenda);
    }
    if (item.personal) {
        parts.push(lang('mambo binafsi', 'Personal isuues'));
    }
    if (item.bill_id && item.bill_name) {
        parts.push(`<a href="/salepurchase/viewVendor?v=${item.bill_id}">${item.bill_name}</a>`);
    }
    if (item.trsp_bill_id && item.trsp_bill_name) {
        parts.push(`<a href="/salepurchase/viewTransporter?t=${item.trsp_bill_id}">${item.trsp_bill_name}</a>`);
    }
    if (!parts.length) {
        return '<span class="text-muted">---</span>';
    }
    return `<span class="px-2 text-primary">${parts.join(' ')}</span>`;
};

const psRenderPartyCell = (item) => {
    if (item.direction === 'in') {
        return psRenderFromCell(item);
    }
    if (item.direction === 'out') {
        return psRenderToCell(item);
    }
    return '<span class="text-muted">---</span>';
};

const psRenderWekaDescription = (item) => {
    let html = '';

    if (item.customer_id && item.customer_name) {
        const label = item.cd_order_id
            ? lang('Malipo ya order kwa ', 'Order payment from ')
            : lang('Malipo ya ankara mauzo ya mafuta kutoka kwa ', 'Invoice payment Fuel sales from ');
        html += `${label}<a href="/salepurchase/ViewCustomer?i=${item.customer_id}">${psTitleCase(item.customer_name)}</a> `;
    }

    if (item.shift_id && !item.bifore_shift) {
        html += lang('mauzo ya mafuta kutoka zamu ', 'Fuel sales from shift ');
        html += `<a href="/salepurchase/viewShift?i=${item.shift_id}">SH-${item.shift_code || ''}</a> `;
        html += lang('na ', 'by ');
        html += `<span class="bluePrint">${psTitleCase(item.shift_by_name || '')}</span> `;
    }

    if (item.bifore_shift && item.shift_id) {
        html += lang('Kuchukua pesa kutoka zamu ', 'Cash Deposit before ');
        html += `<a href="/salepurchase/viewShift?i=${item.shift_id}">SH-${item.shift_code || ''}</a> `;
    }

    if (item.maelezo) {
        html += `<span class="brown">${item.maelezo}</span>`;
    }

    if (!html.trim()) {
        if (item.mobile_pay && item.customer_name) {
            html = `${lang('Malipo kwa simu kutoka kwa ', 'Mobile payment from ')}<span class="bluePrint">${psTitleCase(item.customer_name)}</span>`;
        } else if (item.kuhamisha && item.kutoka) {
            html = `${lang('Uhamisho wa pesa kutoka ', 'Cash transfer from ')}<span class="bluePrint">${item.kutoka}</span>`;
        } else if (item.huduma) {
            html = lang('Malipo ya huduma', 'Service payment');
        } else if (item.payment_type === 'pump_attendant' && item.shift_id) {
            html = `${lang('Malipo ya pump attendant zamu ', 'Pump attendant payment shift ')}<a href="/salepurchase/viewShift?i=${item.shift_id}">SH-${item.shift_code || ''}</a>`;
        } else if (item.payment_type === 'cash_deposit') {
            html = lang('Kuweka pesa kabla ya zamu', 'Cash deposit before shift');
        } else if (item.payment_type === 'bank_deposit') {
            html = lang('Kuweka benki', 'Bank deposit');
        } else {
            html = lang('Mapokezi ya pesa', 'Cash received');
        }
    }

    return html.trim() || '<span class="text-muted">---</span>';
};

const psRenderToaDescription = (item) => {
    if (item.bill_id && item.bill_name) {
        return `${lang('Malipo, Manunuzi ya Mafuta kutoka ', 'Fuel Purcheses Payment from ')}<a href="/salepurchase/viewVendor?v=${item.bill_id}">${item.bill_name}</a>`;
    }

    if (item.maelezo) {
        return `<small>${item.maelezo}</small>`;
    }

    if (item.matumizi_id || item.expense_name) {
        return `<small>${psTitleCase(item.expense_name) || lang('Matumizi', 'Expense')}</small>`;
    }

    if (item.trsp_bill_id && item.trsp_bill_name) {
        return `<small>${lang('Malipo ya bili ya transporter ', 'Transporter bill payment ')}${item.trsp_bill_name}</small>`;
    }

    if (item.personal) {
        return `<small>${lang('Mambo binafsi', 'Personal issues')}</small>`;
    }

    if (item.kuhamisha && item.kwenda) {
        return `<small>${lang('Uhamisho wa pesa kwenda ', 'Cash transfer to ')}${item.kwenda}</small>`;
    }

    if (item.payment_type === 'bill_payment') {
        return `<small>${lang('Malipo ya bili', 'Bill payment')}</small>`;
    }

    return '<span class="text-muted">---</span>';
};

const psRenderDescriptionCell = (item) => {
    const content = item.direction === 'in'
        ? psRenderWekaDescription(item)
        : psRenderToaDescription(item);
    return `<td class="text-left px-2">${content}</td>`;
};

const psPostData = (extra = {}) => {
    const filters = psFilters();
    return {
        account: filters.account,
        recordedBy: filters.recordedBy,
        paymentType: filters.paymentType,
        direction: filters.direction,
        station: filters.st,
        ...extra,
    };
};

const psFindRow = (data) => {
    if (data.key) {
        return psPayData.find((d) => d.key === data.key);
    }
    return psPayData.find((d) => !d.key && d.tFr === data.tFr && d.tTo === data.tTo && d.rname === data.rname);
};

const psArrayCreate = (data) => {
    const existing = psFindRow(data);
    if (existing) {
        Object.assign(existing, data, { loaded: false, transactions: [] });
        return existing;
    }
    const row = {
        id: psPayData.length + 1,
        loaded: false,
        transactions: [],
        ...data,
    };
    psPayData.push(row);
    return row;
};

const psCreateTr = () => {
    let tr = '';
    psPayData.forEach((d) => {
        const summary = d.summary || {};
        const recCount = Number(summary.count_in || 0) + Number(summary.count_out || 0);
        tr += `<tr data-report="${d.id}" class="smallFont cursor-pointer moreDetails">
            <td><a type="button" data-report="${d.id}" class="moreDetails bluePrint">${d.rname}</a></td>
            <td>${psFormatNumber(recCount)}</td>
            <td class="green">${psFormatNumber(summary.received)}</td>
            <td class="brown">${psFormatNumber(summary.paid)}</td>
            <td>${psFormatNumber(summary.net)}</td>
        </tr>`;
    });
    $('#paymentSummaryBody').html(tr);
};

const psLoadSummaryRow = ({ tFr, tTo, rname, key = '' }) => {
    $('#loadMe').modal('show');
    return POSTREQUEST({
        url: '/accounting/paymentStatementData',
        data: psPostData({ tFr, tTo, summaryOnly: 1 }),
    }).then((resp) => {
        $('#loadMe').modal('hide');
        hideLoading();
        if (!resp.success) {
            toastr.error(lang(resp.swa, resp.eng), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
            return null;
        }
        psArrayCreate({
            key,
            rname,
            tFr,
            tTo,
            summary: resp.summary || {},
        });
        psCreateTr();
        return psFindRow({ key, tFr, tTo, rname });
    }).catch(() => {
        $('#loadMe').modal('hide');
        hideLoading();
        return null;
    });
};

const psLoadDetails = (row) => {
    if (!row) return Promise.resolve();
    row.loaded = false;
    $('#loadMe').modal('show');
    return POSTREQUEST({
        url: '/accounting/paymentStatementData',
        data: psPostData({ tFr: row.tFr, tTo: row.tTo }),
    }).then((resp) => {
        $('#loadMe').modal('hide');
        hideLoading();
        if (!resp.success) {
            toastr.error(lang(resp.swa, resp.eng), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
            return;
        }
        row.summary = resp.summary || {};
        row.transactions = resp.transactions || [];
        row.loaded = true;
        psRenderPaymentDetails(row);
    }).catch(() => {
        $('#loadMe').modal('hide');
        hideLoading();
    });
};

const psRenderPaymentDetails = (row) => {
    psActiveRowId = row.id;
    const modalTitle = lang('Taarifa ya Malipo - ', 'Payment Statement - ')
        + `<span class="bluePrint">${row.rname}</span>`;
    $('#paymentDetailsTitle').html(modalTitle);

    const transactions = row.transactions || [];
    if (!transactions.length) {
        $('#paymentsBody').html(`<tr><td colspan="9" class="text-center text-muted">${lang('Hakuna miamala', 'No transactions found')}</td></tr>`);
    } else {
        let html = '';
        transactions.forEach((item) => {
            html += `<tr>
                <td>${item.date ? moment(item.date).format('DD/MM/YYYY HH:mm') : '-'}</td>
                <td>${item.account_name || '-'}</td>
                <td class="text-right">${psFormatNumber(item.before)}</td>
                ${psAmountCell(item.received_amount, 'green')}
                ${psAmountCell(item.withdrawal_amount, 'brown')}
                <td class="text-right">${psFormatNumber(item.after)}</td>
                <td>${psRenderPartyCell(item)}</td>
                ${psRenderDescriptionCell(item)}
                <td class="text-capitalize">${item.recorded_by || '-'}</td>
            </tr>`;
        });
        $('#paymentsBody').html(html);
    }

    $('#paymentSummary').hide();
    $('#paymentDetails').show();
};

const psCreateArray = (rname, tFr, tTo) => {
    const existing = psFindRow({ tFr, tTo, rname });
    if (existing) {
        toastr.info(lang('tayari ipo', 'already exists'), lang('Taarifa', 'Info'), { timeOut: 2000 });
        return;
    }
    psLoadSummaryRow({ tFr, tTo, rname });
};

const psReloadAll = () => {
    const activeKey = psActiveRowId
        ? (psPayData.find((d) => d.id === psActiveRowId)?.key || null)
        : null;
    const activeCustom = psActiveRowId
        ? psPayData.find((d) => d.id === psActiveRowId)
        : null;

    psPayData = [];
    const { today, week, month } = psFilters();
    $('#loadMe').modal('show');

    return POSTREQUEST({
        url: '/accounting/paymentStatementData',
        data: psPostData({ overview: 1 }),
    }).then((resp) => {
        $('#loadMe').modal('hide');
        hideLoading();
        if (!resp.success) return;

        const overview = resp.overview || {};
        [
            { ...today, summary: overview.today || {} },
            { ...week, summary: overview.week || {} },
            { ...month, summary: overview.month || {} },
        ].forEach((preset) => {
            psArrayCreate({
                key: preset.key,
                rname: preset.rname,
                tFr: preset.tFr,
                tTo: preset.tTo,
                summary: preset.summary,
            });
        });

        psCreateTr();

        if ($('#paymentDetails').is(':visible') && psActiveRowId) {
            let row = null;
            if (activeKey) {
                row = psPayData.find((d) => d.key === activeKey);
            } else if (activeCustom) {
                row = psPayData.find((d) =>
                    !d.key
                    && d.tFr === activeCustom.tFr
                    && d.tTo === activeCustom.tTo
                    && d.rname === activeCustom.rname
                );
            }
            if (row) {
                psLoadDetails(row);
            } else {
                $('#paymentDetails').hide();
                $('#paymentSummary').show();
                psActiveRowId = null;
            }
        }
    }).catch(() => {
        $('#loadMe').modal('hide');
        hideLoading();
    });
};

const psFilterLabel = (selectId, allLabel) => {
    const val = $(selectId).val();
    if (!val || val === '0' || val === '') {
        return allLabel;
    }
    return $(`${selectId} option:selected`).text().trim();
};

const psPrintStyles = `
<style>
    @page { size: landscape; margin: 8mm; }
    #psPrintReport {
        font-family: Arial, Helvetica, sans-serif;
        color: #000;
        font-size: 11px;
        line-height: 1.35;
    }
    .ps-print-title {
        text-align: center;
        font-size: 18px;
        font-weight: 700;
        margin: 6px 0 10px;
    }
    .ps-print-meta {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 10px;
        font-size: 11px;
    }
    .ps-print-meta td {
        padding: 2px 8px 2px 0;
        vertical-align: top;
    }
    .ps-print-meta .ps-label {
        font-weight: 700;
        white-space: nowrap;
        width: 130px;
    }
    .ps-print-meta .ps-val {
        padding-right: 24px;
    }
    .ps-print-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 9.5px;
    }
    .ps-print-table th,
    .ps-print-table td {
        border: 1px solid #333;
        padding: 4px 5px;
        vertical-align: top;
        word-wrap: break-word;
    }
    .ps-print-table th {
        background: #efefef;
        font-weight: 700;
        text-align: left;
    }
    .ps-print-table .text-right { text-align: right; }
    .ps-print-table thead { display: table-header-group; }
    .ps-print-table tr { page-break-inside: avoid; }
    .ps-print-summary-block { page-break-inside: avoid; margin-bottom: 8px; }
    @media print {
        body { margin: 0; padding: 0; }
        #psPrintReport { width: 100%; }
    }
</style>`;

const psStripHtml = (html) => {
    if (!html) return '-';
    const el = document.createElement('div');
    el.innerHTML = html;
    return el.textContent.trim() || '-';
};

const psBuildPrintTableHtml = (transactions) => {
    let body = '';
    transactions.forEach((item) => {
        const received = item.received_amount != null ? psFormatNumber(item.received_amount) : '---';
        const withdrawal = item.withdrawal_amount != null ? psFormatNumber(item.withdrawal_amount) : '---';
        const party = psStripHtml(psRenderPartyCell(item));
        const description = psStripHtml(
            item.direction === 'in' ? psRenderWekaDescription(item) : psRenderToaDescription(item)
        );
        body += `<tr>
            <td>${item.date ? moment(item.date).format('DD/MM/YYYY HH:mm') : '-'}</td>
            <td>${item.account_name || '-'}</td>
            <td class="text-right">${psFormatNumber(item.before)}</td>
            <td class="text-right">${received}</td>
            <td class="text-right">${withdrawal}</td>
            <td class="text-right">${psFormatNumber(item.after)}</td>
            <td>${party}</td>
            <td>${description}</td>
            <td class="text-capitalize">${item.recorded_by || '-'}</td>
        </tr>`;
    });

    return `<table class="ps-print-table">
        <thead>
            <tr>
                <th style="width:9%">${lang('Tarehe', 'Date')}</th>
                <th style="width:10%">${lang('Akaunti', 'Account')}</th>
                <th style="width:8%" class="text-right">${lang('Kabla', 'Before')}</th>
                <th style="width:8%" class="text-right">${lang('Mapokezi', 'Received')}</th>
                <th style="width:8%" class="text-right">${lang('Kutoa', 'Withdrawal')}</th>
                <th style="width:8%" class="text-right">${lang('Baada', 'After')}</th>
                <th style="width:11%">${lang('Kutoka', 'From')} / ${lang('Kwenda', 'To')}</th>
                <th style="width:28%">${lang('Maelezo', 'Description')}</th>
                <th style="width:10%">${lang('Aliyerekebisha', 'Recorded By')}</th>
            </tr>
        </thead>
        <tbody>${body}</tbody>
    </table>`;
};

const psBuildPrintReport = () => {
    const row = psPayData.find((d) => d.id === psActiveRowId);
    if (!row || !row.transactions?.length) {
        toastr.info(lang('Hakuna data ya kuchapisha', 'No data to print'), lang('Taarifa', 'Info'), { timeOut: 2000 });
        return null;
    }

    const filters = psFilters();
    const ddiff = moment(row.tTo).diff(moment(row.tFr), 'days');
    const period = ddiff > 0
        ? `${moment(row.tFr).format('DD/MM/YYYY HH:mm')} - ${moment(row.tTo).format('DD/MM/YYYY HH:mm')}`
        : moment(row.tTo).format('DD/MM/YYYY HH:mm');

    const summary = row.summary || {};
    const userN = $('#user_userName').val() || '';
    const stationLabel = filters.st
        ? ($('#stationFilter option:selected').data('stxn') || $('#stationFilter option:selected').text().trim())
        : lang('Vituo Vyote', 'All Stations');

    const filterDetails = `
        <div class="ps-print-summary-block">
            <div class="ps-print-title">${lang('Taarifa ya Malipo', 'Payment Statement')}: ${row.rname} (${period})</div>
            <table class="ps-print-meta">
                <tr>
                    <td class="ps-label">${lang('Kituo', 'Station')}:</td>
                    <td class="ps-val">${stationLabel}</td>
                    <td class="ps-label">${lang('Mapokezi', 'Received')}:</td>
                    <td class="ps-val">${psFormatNumber(summary.received)}</td>
                </tr>
                <tr>
                    <td class="ps-label">${lang('Akaunti', 'Account')}:</td>
                    <td class="ps-val">${psFilterLabel('#psAccountFilter', lang('Akaunti Zote', 'All Accounts'))}</td>
                    <td class="ps-label">${lang('Malipo', 'Paid')}:</td>
                    <td class="ps-val">${psFormatNumber(summary.paid)}</td>
                </tr>
                <tr>
                    <td class="ps-label">${lang('Aliyerekebisha', 'Recorded By')}:</td>
                    <td class="ps-val text-capitalize">${psFilterLabel('#psRecordedByFilter', lang('Wote', 'All'))}</td>
                    <td class="ps-label">${lang('Salio', 'Net')}:</td>
                    <td class="ps-val">${psFormatNumber(summary.net)}</td>
                </tr>
                <tr>
                    <td class="ps-label">${lang('Aina ya Malipo', 'Payment Type')}:</td>
                    <td class="ps-val">${filters.paymentType ? psTypeLabel(filters.paymentType) : lang('Zote', 'All')}</td>
                    <td class="ps-label">${lang('Imetolewa', 'Issued on')}:</td>
                    <td class="ps-val">${moment().format('DD/MM/YYYY HH:mm')}</td>
                </tr>
                <tr>
                    <td class="ps-label">${lang('Mwelekeo', 'Direction')}:</td>
                    <td class="ps-val">${
                        filters.direction === 'in'
                            ? lang('Mapokezi', 'Received')
                            : filters.direction === 'out'
                                ? lang('Malipo', 'Paid Out')
                                : lang('Zote', 'All')
                    }</td>
                    <td class="ps-label">${lang('Imetolewa na', 'Issued by')}:</td>
                    <td class="ps-val text-capitalize">${userN}</td>
                </tr>
            </table>
        </div>`;

    return filterDetails + psBuildPrintTableHtml(row.transactions);
};

$(document).ready(() => {
    psReloadAll();

    $('body').on('click', '.moreDetails', function () {
        const val = Number($(this).data('report'));
        const row = psPayData.find((d) => d.id === val);
        if (!row) return;
        psLoadDetails(row);
    });

    $('#backToSummary').on('click', function () {
        psActiveRowId = null;
        $('#paymentDetails').hide();
        $('#paymentSummary').show();
    });

    $('#customDateSubmit').on('click', function () {
        const rname = $('#durationName').val().trim();
        const startDate = $('#startDate').val();
        const endDate = $('#endDate').val();
        if (!rname || !startDate || !endDate) return;
        $('#durationModal').modal('hide');
        psCreateArray(
            rname,
            moment(startDate).startOf('day').format(),
            moment(endDate).endOf('day').format(),
        );
    });

    $('#stationFilter, #psAccountFilter, #psRecordedByFilter, #psTypeFilter, #psDirectionFilter').change(function () {
        psReloadAll();
    });

    $('#printPaymentStatement').on('click', function () {
        const reportData = psBuildPrintReport();
        if (!reportData) return;

        openAndPrintDocument(`<div id="psPrintReport">${reportData}</div>`, { extraHead: psPrintStyles });
    });
});
