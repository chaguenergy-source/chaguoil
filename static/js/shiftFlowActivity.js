let flowData = [];
let activeDetail = null;
let isAdmin = false;
let shiftAttachmentsData = [];
let shiftAttLayout = 1;

const flowConfig = window.shiftFlowConfig || {};
const mode = flowConfig.mode || 'transfer';
const endpoint = flowConfig.endpoint || '';
const approveEndpoint = '/salepurchase/approveFuelActivity';
const deleteEndpoint = flowConfig.deleteEndpoint || '';

const parentIdField = () => (mode === 'transfer' ? 'transfer_id' : mode === 'receive' ? 'receive_id' : 'adj_id');

const escapeShiftHtml = text => {
    if (text === null || text === undefined) return '';
    return String(text).replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
};

const uniqueAttachments = items => {
    const seen = new Set();
    return (items || []).filter(item => {
        if (!item || seen.has(item.id)) return false;
        seen.add(item.id);
        return true;
    });
};

const getAttachmentsForRows = (rows, attachmentList) => {
    const parentIds = new Set((rows || []).map(r => r[parentIdField()]).filter(Boolean));
    return uniqueAttachments((attachmentList || []).filter(a => parentIds.has(a.parent_id)));
};

const getAttachmentsForParent = (parentId, attachmentList) => {
    return uniqueAttachments((attachmentList || []).filter(a => Number(a.parent_id) === Number(parentId)));
};

const isPdfFile = url => /\.pdf(\?|$)/i.test(String(url || ''));

const attachmentPreviewUrl = att => att.embed_url || att.file || '';

const buildAttachmentPreview = att => {
    const fileUrl = escapeShiftHtml(att.file || '');
    const previewUrl = escapeShiftHtml(attachmentPreviewUrl(att));
    if (!previewUrl) return `<div class="p-3 text-muted small">${lang('Hakuna faili', 'No file')}</div>`;
    if (isPdfFile(att.file || att.embed_url)) {
        return `
          <iframe src="${previewUrl}" title="${escapeShiftHtml(att.attach_name || 'PDF')}"></iframe>
          <div class="text-center py-2 border-top">
            <a href="${fileUrl}" target="_blank" rel="noopener" class="btn btn-outline-primary btn-sm">${lang('Fungua PDF','Open PDF')}</a>
          </div>`;
    }
    return `<img src="${fileUrl || previewUrl}" alt="${escapeShiftHtml(att.attach_name || 'Attachment')}" loading="lazy">`;
};

const buildAttachmentCell = (parentId, attachmentList) => {
    const items = getAttachmentsForParent(parentId, attachmentList);
    if (!items.length) return '<span class="text-muted small">—</span>';
    return `<button type="button" class="btn btn-outline-info btn-sm py-0 px-2 shift-att-btn" data-parent-id="${parentId}">${items.length} ${lang('viambatisho', 'attachments')}</button>`;
};

const buildShiftAttachmentItemHtml = att => {
    const title = att.attach_name || lang('Kiambatisho', 'Attachment');
    const dateText = att.date ? moment(att.date).format('DD/MM/YYYY HH:mm') : '';
    const docType = att.printedDocu ? lang('Dokument iliyosainiwa', 'Signed document') : lang('Kiambatisho', 'Attachment');
    const meta = `${escapeShiftHtml(title)} · ${docType}${dateText ? ` · ${dateText}` : ''}`;
    return `
      <div class="shift-att-item">
        <div class="shift-att-meta">${meta}</div>
        ${buildAttachmentPreview(att)}
      </div>
    `;
};

const renderShiftAttachmentsGallery = () => {
    const gallery = document.getElementById('shiftAttachmentsGallery');
    const emptyEl = document.getElementById('shiftAttachmentsEmpty');
    if (!gallery) return;

    gallery.className = `shift-att-gallery layout-${shiftAttLayout}`;

    if (!shiftAttachmentsData.length) {
        gallery.innerHTML = '';
        if (emptyEl) emptyEl.style.display = 'block';
        return;
    }

    if (emptyEl) emptyEl.style.display = 'none';

    const perPage = Number(shiftAttLayout) || 1;
    let html = '';
    for (let i = 0; i < shiftAttachmentsData.length; i += perPage) {
        const pageItems = shiftAttachmentsData.slice(i, i + perPage);
        html += `<div class="shift-att-page">${pageItems.map(buildShiftAttachmentItemHtml).join('')}</div>`;
    }
    gallery.innerHTML = html;
};

const openShiftAttachmentsModal = (items, title) => {
    shiftAttachmentsData = uniqueAttachments(items || []);
    shiftAttLayout = 1;
    $('.shift-att-layout').removeClass('btn-secondary active').addClass('btn-outline-secondary');
    $('.shift-att-layout[data-layout="1"]').addClass('active btn-secondary').removeClass('btn-outline-secondary');
    $('#shiftAttachmentsModalTitle').text(title || lang('Viambatisho', 'Attachments'));
    $('#shiftAttachmentsModalSummary').text(`${shiftAttachmentsData.length} ${lang('viambatisho', 'attachments')}`);
    renderShiftAttachmentsGallery();
    $('#shiftAttachmentsModal').modal('show');
};

const buildShiftAttachmentsPrintHtml = () => {
    const perPage = Number(shiftAttLayout) || 1;
    const modalTitle = $('#shiftAttachmentsModalTitle').text() || lang('Viambatisho', 'Attachments');
    const heading = `<h4 class="text-center mb-2">${escapeShiftHtml(modalTitle)}</h4>
      <p class="text-center small mb-3">${shiftAttachmentsData.length} ${lang('viambatisho', 'attachments')} · ${shiftAttLayout}/${lang('ukurasa', 'page')}</p>`;

    let pagesHtml = '';
    for (let i = 0; i < shiftAttachmentsData.length; i += perPage) {
        const pageItems = shiftAttachmentsData.slice(i, i + perPage);
        pagesHtml += `<div class="print-page layout-${shiftAttLayout}">${pageItems.map(att => `
          <div class="print-item">
            <div class="print-meta">${escapeShiftHtml(att.attach_name || '')}${att.date ? ` · ${moment(att.date).format('DD/MM/YYYY HH:mm')}` : ''}</div>
            ${isPdfFile(att.file || att.embed_url)
                ? `<iframe src="${escapeShiftHtml(attachmentPreviewUrl(att))}" style="width:100%;height:240mm;border:0;"></iframe>`
                : `<img src="${escapeShiftHtml(att.file || attachmentPreviewUrl(att))}" alt="">`}
          </div>
        `).join('')}</div>`;
    }

    return `
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
      ${heading}${pagesHtml}
    `;
};

const updateAllAttachmentsButton = (rows, attachmentList) => {
    const items = getAttachmentsForRows(rows, attachmentList);
    const btn = $('#viewAllAttachmentsBtn');
    const countEl = $('#allAttachmentsCount');
    if (!btn.length) return;
    countEl.text(items.length);
    btn.prop('disabled', items.length === 0);
    btn.toggle(items.length > 0);
};

const activityTypeMap = {
    transfer: 'transfer',
    receive: 'receive',
    adjustment: 'adjustment'
};

const getSelectedUnapprovedIds = () => $('.selectRecord:checked').filter(function () {
    return !$(this).is(':disabled');
}).map(function () {
    return $(this).data('id');
}).get();

const updateActionButtons = () => {
    const selected = getSelectedUnapprovedIds();
    $('#approveAllBtn').prop('disabled', selected.length === 0);
    $('#unapprovedCount').text(selected.length);
    if (mode === 'receive' && deleteEndpoint) {
        $('#deleteReceiveBtn').prop('disabled', selected.length === 0);
        $('#deleteSelectedCount').text(selected.length);
    }
};

const filters = () => {
    const st = Number($('#stationFilter').val() || 0);
    const today = { rname: lang('Leo', 'Today'), tFr: moment().startOf('day').format(), tTo: moment().format() };
    const week = { rname: lang('Wiki hii', 'This Week'), tFr: moment().startOf('isoWeek').format(), tTo: moment().format() };
    const month = { rname: lang('Mwezi huu', 'This Month'), tFr: moment().startOf('month').format(), tTo: moment().format() };
    return { st, today, week, month };
};

const loadRecords = ({ tFr, tTo, rname, init }) => {
    if (!endpoint) {
        return;
    }

    $('#loadMe').modal('show');
    const data = { tFr, tTo };
    const req = POSTREQUEST({ data, url: endpoint });

    req.then(res => {
        $('#loadMe').modal('hide');
        hideLoading();
        if (res.success) {
            isAdmin = res.isadmin;
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
        addDurationRecords({ records: resp.records, attachments: resp.attachments, ...today });
        addDurationRecords({ records: resp.records, attachments: resp.attachments, ...week });
    }

    addDurationRecords({ records: resp.records, attachments: resp.attachments, tFr, tTo, rname });
    renderSummary();
};

const addDurationRecords = ({ records, attachments, tFr, tTo, rname }) => {
    const isThere = flowData.find(d => d.tFr === tFr && d.tTo === tTo && d.rname === rname);
    if (isThere) {
        return;
    }

    const filtered = (records || []).filter(r => moment(r.tarehe).format() >= tFr && moment(r.tarehe).format() <= tTo);
    const filteredAttachments = getAttachmentsForRows(filtered, attachments);

    flowData.push({
        id: flowData.length + 1,
        rname,
        tFr,
        tTo,
        records: filtered,
        attachments: filteredAttachments
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
        addDurationRecords({ records: parent.records, attachments: parent.attachments, tFr, tTo, rname });
        renderSummary();
    } else {
        loadRecords({ tFr, tTo, rname, init: 0 });
    }
}

const renderSummary = () => {
    const { st } = filters();
    let tr = '';

    flowData.forEach(d => {
        const records = st ? d.records.filter(r => Number(r.st) === st) : d.records;
        const totalQty = records.reduce((a, b) => a + Number(b.qty || b.diff || 0), 0);
        const totalWorth = records.reduce((a, b) => a + Number(b.worth || 0), 0);

        tr += `<tr class="smallFont cursor-pointer moreDetails" data-report="${d.id}">
            <td><a type="button" class="bluePrint moreDetails" data-report="${d.id}">${d.rname}</a></td>
            <td>${records.length}</td>
            <td>${formatNumber(totalQty)}</td>
            <td>${formatNumber(totalWorth)}</td>
        </tr>`;
    });

    $('#activitySummaryBody').html(tr);
};

$('body').on('click', '.moreDetails', function () {
    const id = Number($(this).data('report'));
    const data = flowData.find(d => d.id === id);
    if (!data) {
        return;
    }
    activeDetail = data;
    renderDetails(data);
});

$('#backToSummary').on('click', function () {
    $('#paymentDetails').hide();
    $('#paymentSummary').show();
    $('#approveAllBtn').prop('disabled', true);
    $('#deleteReceiveBtn').prop('disabled', true);
    $('#unapprovedCount').text('0');
    $('#deleteSelectedCount').text('0');
    $('#selectAllRecords').prop('checked', false);
    $('#viewAllAttachmentsBtn').hide().prop('disabled', true);
    $('#allAttachmentsCount').text('0');
});

const renderDetails = data => {
    const { st } = filters();
    const rows = st ? data.records.filter(r => Number(r.st) === st) : data.records;
    const titleMap = {
        transfer: lang('Maelezo ya Transfer - ', 'Transfer Details - '),
        receive: lang('Maelezo ya Receive - ', 'Receives Details - '),
        adjustment: lang('Maelezo ya Adjustment - ', 'Adjustments Details - ')
    };

    const unapprovedCount = rows.filter(r => !r.adminAproval).length;

    const attachmentList = data.attachments || [];
    let tr = '';
    rows.forEach((r, idx) => {
        const approved = r.adminAproval;
        const approvalStatus = approved
            ? `<span class="badge badge-success">${lang('Imehakikiwa','Approved')}</span>`
            : `<span class="badge badge-warning">${lang('Haijahakikiwa','Unapproved')}</span>`;
        const parentId = r[parentIdField()];
        const attachmentCell = buildAttachmentCell(parentId, attachmentList);

        const checkboxCell = isAdmin
            ? `<td class="text-center"><input type="checkbox" class="selectRecord cursor-pointer" ${approved ? 'checked disabled' : ''} data-id="${r.id}"></td>`
            : '';

        if (mode === 'transfer') {
            tr += `<tr class="smallFont">
                ${checkboxCell}
                <td>${idx + 1}</td>
                <td>${moment(r.tarehe).format('DD/MM/YYYY HH:mm')}</td>
                <td>${r.stN || ''}</td>
                <td><a href="/salepurchase/viewTransfer?i=${r.transfer_id}">TFR-${r.transfer_code || ''}</a></td>
                <td>${r.fuel_name || ''}</td>
                <td>${r.from_tank || '-'}</td>
                <td>${r.to_tank || '-'}</td>
                <td>${formatNumber(r.qty || 0)}</td>
                <td>${formatNumber(r.cost || 0)}</td>
                <td>${formatNumber(r.worth || 0)}</td>
                <td>${attachmentCell}</td>
                <td>${approvalStatus}</td>
            </tr>`;
        }

        if (mode === 'receive') {
            let fromLabel;
            if (r.from_purchase_id) {
                fromLabel = `<a href="/salepurchase/viewPurchase?i=${r.from_purchase_id}">${lang('Manunuzi','Purchase')} PU-${r.from_purchase_code || ''}</a>`;
            } else if (r.from_transf_id) {
                fromLabel = `<a href="/salepurchase/viewTransfer?i=${r.from_transf_id}">${lang('Kuhamishwa','Transfer')} TFR-${r.from_transf_code || ''}</a>`;
            } else {
                fromLabel = r.from_tank || '-';
            }
            tr += `<tr class="smallFont">
                ${checkboxCell}
                <td>${idx + 1}</td>
                <td>${moment(r.tarehe).format('DD/MM/YYYY HH:mm')}</td>
                <td>${r.stN || ''}</td>
                <td><a href="/salepurchase/viewFuelReceive?i=${r.receive_id}">TTR-${r.receive_code || ''}</a></td>
                <td>${r.fuel_name || ''}</td>
                <td>${fromLabel}</td>
                <td>${r.to_tank || '-'}</td>
                <td>${formatNumber(r.qty || 0)}</td>
                <td>${formatNumber(r.worth || 0)}</td>
                <td>${attachmentCell}</td>
                <td>${approvalStatus}</td>
            </tr>`;
        }

        if (mode === 'adjustment') {
            tr += `<tr class="smallFont">
                ${checkboxCell}
                <td>${idx + 1}</td>
                <td>${moment(r.tarehe).format('DD/MM/YYYY HH:mm')}</td>
                <td>${r.stN || ''}</td>
                <td><a href="/salepurchase/adjView?i=${r.adj_id}">ADJ-${r.adj_code || ''}</a></td>
                <td>${r.tank_name || ''}</td>
                <td>${r.fuel_name || ''}</td>
                <td>${formatNumber(r.read || 0)}</td>
                <td>${formatNumber(r.stick || 0)}</td>
                <td>${formatNumber(r.diff || 0)}</td>
                <td>${formatNumber(r.worth || 0)}</td>
                <td>${attachmentCell}</td>
                <td>${approvalStatus}</td>
            </tr>`;
        }
    });

    const totalQty = rows.reduce((a, b) => a + Number(b.qty || b.diff || 0), 0);
    const totalWorth = rows.reduce((a, b) => a + Number(b.worth || 0), 0);
    const approvedCount = rows.filter(r => r.adminAproval).length;
    const approvalText = `${approvedCount}/${rows.length} ${lang('uhakiki', 'approval')}`;
    const labelColspan = {
        transfer: isAdmin ? 8 : 7,
        receive: isAdmin ? 8 : 7,
        adjustment: isAdmin ? 9 : 8
    };

    if (mode === 'transfer') {
        tr += `<tr class="smallFont font-weight-bold">
            <td colspan="${labelColspan.transfer}">${lang('Jumla', 'Total')}</td>
            <td>${formatNumber(totalQty)}</td>
            <td>-</td>
            <td>${formatNumber(totalWorth)}</td>
            <td>-</td>
            <td>${approvalText}</td>
        </tr>`;
    } else {
        const col = mode === 'receive' ? labelColspan.receive : labelColspan.adjustment;
        tr += `<tr class="smallFont font-weight-bold">
            <td colspan="${col}">${lang('Jumla', 'Total')}</td>
            <td>${formatNumber(totalQty)}</td>
            <td>${formatNumber(totalWorth)}</td>
            <td>-</td>
            <td>${approvalText}</td>
        </tr>`;
    }

    $('#activityDetailsTitle').html(titleMap[mode] + `<span class="bluePrint">${data.rname}</span>`);
    $('#activityDetailsBody').html(tr);
    updateAllAttachmentsButton(rows, attachmentList);
    updateActionButtons();
    // toggle approve button visibility
    $('#approveAllBtn').toggle(isAdmin);
    if (mode === 'receive' && deleteEndpoint) {
        $('#deleteReceiveBtn').toggle(isAdmin);
    }
    $('#paymentSummary').hide();
    $('#paymentDetails').show();
};

$('#stationFilter').on('change', function () {
    renderSummary();
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

    const modeTitle = {
        transfer: lang('Miamala ya Transfer', 'Transfer Activity'),
        receive: lang('Miamala ya Receive', 'Receives Activity'),
        adjustment: lang('Miamala ya Adjustment', 'Adjustments Activity')
    };

    const heading = `<h2>${modeTitle[mode] || lang('Ripoti', 'Report')}: ${reportDuration}</h2>`;
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

    // Print exactly the same table structure shown on screen to preserve column alignment.
    const theReportData = document.getElementById('paymentsTable').innerHTML;
    const reportData = heading + statementDetails + theReportData;
    const printWindow = window.open('', '', 'height=600,width=1000');
    printWindow.document.write(company_header);
    printWindow.document.write(`${reportData}`);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();
});

const docLabelForMode = (r, parentId) => {
    if (mode === 'transfer') return `TFR-${r.transfer_code || parentId}`;
    if (mode === 'receive') return `TTR-${r.receive_code || parentId}`;
    return `ADJ-${r.adj_code || parentId}`;
};

$('body').on('click', '.shift-att-btn', function (e) {
    e.preventDefault();
    e.stopPropagation();
    if (!activeDetail) return;

    const parentId = Number($(this).data('parent-id'));
    const items = getAttachmentsForParent(parentId, activeDetail.attachments);
    const row = (activeDetail.records || []).find(r => Number(r[parentIdField()]) === parentId);
    const docLabel = row ? docLabelForMode(row, parentId) : String(parentId);
    openShiftAttachmentsModal(items, docLabel);
});

$('#viewAllAttachmentsBtn').on('click', function () {
    if (!activeDetail) return;

    const { st } = filters();
    const rows = st ? activeDetail.records.filter(r => Number(r.st) === st) : activeDetail.records;
    const items = getAttachmentsForRows(rows, activeDetail.attachments);
    const title = `${lang('Viambatisho - ', 'Attachments - ')}${activeDetail.rname}`;
    openShiftAttachmentsModal(items, title);
});

$('body').on('click', '.shift-att-layout', function () {
    shiftAttLayout = Number($(this).data('layout')) || 1;
    $('.shift-att-layout').removeClass('btn-secondary active').addClass('btn-outline-secondary');
    $(this).addClass('active btn-secondary').removeClass('btn-outline-secondary');
    renderShiftAttachmentsGallery();
});

$('#printShiftAttachments').on('click', function () {
    if (!shiftAttachmentsData.length) {
        toastr.info(lang('Hakuna viambatisho vya kuchapisha', 'No attachments to print'), lang('Taarifa', 'Info'), { timeOut: 2000 });
        return;
    }

    const printWindow = window.open('', '', 'height=800,width=1000');
    printWindow.document.write('<html><head><title>Attachments</title></head><body>');
    printWindow.document.write(buildShiftAttachmentsPrintHtml());
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => printWindow.print(), 700);
});

// Checkbox selection for approve / delete
$('body').on('change', '.selectRecord, #selectAllRecords', function () {
    const isCheckAll = $(this).is('#selectAllRecords');
    if (isCheckAll) {
        const checked = $(this).is(':checked');
        $('.selectRecord').each(function () {
            if (!$(this).is(':disabled')) $(this).prop('checked', checked);
        });
    }
    updateActionButtons();
});

// Confirm approve
$('#confirmApproveRecords').on('click', function () {
    const ids = getSelectedUnapprovedIds();

    if (!ids.length) return;

    $('#confirmApprovalModal').modal('hide');
    $('#loadMe').modal('show');

    const data = {
        item_ids: JSON.stringify(ids),
        activity: activityTypeMap[mode]
    };

    const req = POSTREQUEST({ data, url: approveEndpoint });
    req.then(res => {
        $('#loadMe').modal('hide');
        hideLoading();
        if (res.success) {
            toastr.success(lang('Imehakikiwa kwa mafanikio', 'Approved successfully'), lang('Imekamilika', 'Success'), { timeOut: 2000 });
            // mark rows as approved in local data
            ids.forEach(id => {
                flowData.forEach(d => {
                    const rec = d.records.find(r => r.id === id);
                    if (rec) rec.adminAproval = true;
                });
            });
            if (activeDetail) renderDetails(activeDetail);
        } else {
            toastr.error(lang(res.swa, res.eng), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
        }
    }).catch(() => {
        $('#loadMe').modal('hide');
        hideLoading();
        toastr.error(lang('Tatizo la mtandao', 'Network error'), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
    });
});

// Confirm delete (receive mode only)
$('#confirmDeleteRecords').on('click', function () {
    if (mode !== 'receive' || !deleteEndpoint) return;

    const ids = getSelectedUnapprovedIds();
    if (!ids.length) return;

    $('#confirmDeleteModal').modal('hide');
    $('#loadMe').modal('show');

    const data = { item_ids: JSON.stringify(ids) };
    const req = POSTREQUEST({ data, url: deleteEndpoint });

    req.then(res => {
        $('#loadMe').modal('hide');
        hideLoading();
        if (res.success) {
            toastr.success(lang('Imefutwa na stock imerejeshwa', 'Deleted and stock restored'), lang('Imekamilika', 'Success'), { timeOut: 2000 });
            const idSet = new Set(ids.map(Number));
            flowData.forEach(d => {
                d.records = d.records.filter(r => !idSet.has(Number(r.id)));
            });
            if (activeDetail) {
                activeDetail.records = activeDetail.records.filter(r => !idSet.has(Number(r.id)));
                if (activeDetail.records.length) {
                    renderDetails(activeDetail);
                } else {
                    $('#backToSummary').click();
                    renderSummary();
                }
            } else {
                renderSummary();
            }
        } else {
            toastr.error(lang(res.swa, res.eng), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
        }
    }).catch(() => {
        $('#loadMe').modal('hide');
        hideLoading();
        toastr.error(lang('Tatizo la mtandao', 'Network error'), lang('Haikufanikiwa', 'Error'), { timeOut: 2000 });
    });
});
