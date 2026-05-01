let payData = [], isAdmin = false, payId = 0, useData = {};

const filters = () => {
	const st = Number($('#stationFilter').val()),
		source = $('#paymentSourceFilter').val() || 'all',
		today = { rname: lang('Leo', 'Today'), tFr: moment(moment().startOf('day')).format(), tTo: moment().format() },
		week = { rname: lang('Wiki hii', 'This Week'), tFr: moment(moment().startOf('isoWeek')).format(), tTo: moment().format() },
		month = { rname: lang('Mwezi huu', 'This Month'), tFr: moment(moment().startOf('month')).format(), tTo: moment().format() };

	return { st, source, today, week, month };
};

const filterBySource = payments => {
	const { source } = filters();
	if (source === 'all') {
		return payments;
	}
	return payments.filter(payment => payment.payment_source === source);
};

const paymentSourceLabel = payment => {
	if (payment.payment_source === 'pump_attendant') {
		return lang('Mhudumu wa Pampu', 'Pump Attendant');
	}
	if (payment.payment_source === 'payment_account') {
		return lang('Akaunti ya Malipo', 'Payment Account');
	}
	return lang('Haijulikani', 'Unknown');
};

const loadExpenses = d => {
	$('#loadMe').modal('show');

	const { tFr, tTo, rname, init } = d;
	const savedIds = JSON.parse(sessionStorage.getItem('exp_Ids')) || [];
	const savedObjects = JSON.parse(sessionStorage.getItem('simplifiedExpenseObjects')) || [];
	let data = { tFr, tTo };

	if (savedIds.length > 0 && savedObjects.length > 0) {
		data = {
			...data,
			from_session: 1,
			exp_Ids: JSON.stringify(savedIds)
		};
	}

	const req = POSTREQUEST({ data, url: '/salepurchase/getShiftExpenses' });
	req.then(res => {
		$('#loadMe').modal('hide');
		hideLoading();
		if (res.success) {
			sessionStorage.removeItem('exp_Ids');
			sessionStorage.removeItem('simplifiedExpenseObjects');
			isAdmin = res.isadmin;
			renderExpenses({ resp: res, rname, init, tFr, tTo, savedObjects });
		} else {
			toastr.error(lang(res.swa, res.eng), lang('Haikufanikiwa', 'Error '), { timeOut: 2000 });
		}
	}).catch(() => {
		$('#loadMe').modal('hide');
		hideLoading();
		toastr.error(lang('Tatizo la mtandao, jaribu tena', 'Network error, try again'), lang('Haikufanikiwa', 'Error '), { timeOut: 2000 });
	});
};

$(document).ready(() => {
	const { month } = filters(),
		{ tFr, tTo, rname } = month;
	loadExpenses({ tFr, tTo, rname, init: 1 });
});

const renderExpenses = d => {
	const { resp, rname, init, tFr, tTo, savedObjects } = d,
		{ today, week } = filters();

	if (savedObjects.length && init) {
		savedObjects.forEach(so => {
			const { tFr, tTo, rname } = so;
			createArray(rname, tFr, tTo);
		});
		createTr();
		return;
	}

	if (init) {
		ArryCreate({ ...resp, tFr: today.tFr, tTo: today.tTo, rname: today.rname });
		ArryCreate({ ...resp, tFr: week.tFr, tTo: week.tTo, rname: week.rname });
	}

	ArryCreate({ ...resp, tFr, tTo, rname });
	createTr();
};

const ArryCreate = d => {
	const { tFr, tTo, rname } = d,
		expenses = d.expenses?.filter(s => moment(s.tarehe).format() >= tFr && moment(s.tarehe).format() <= tTo),
		thedt = {
			id: payData.length + 1,
			rname,
			tFr,
			tTo,
			payments: expenses
		};
	payData.push(thedt);
};

function createArray(rname, tFr, tTo) {
	const saDt = payData.filter(d => d.tFr <= tFr && d.tTo >= tTo),
		isThere = payData.filter(d => d.tFr === tFr && d.tTo === tTo),
		msg = lang('tayari ipo', 'already exists');

	if (isThere.length) {
		toastr.info(msg, lang('Taarifa', 'info '), { timeOut: 2000 });
		return;
	}

	if (saDt.length > 0) {
		const { payments } = saDt[0],
			dt = { payments, tFr, tTo, rname };
		ArryCreate(dt);
		createTr();
	} else {
		loadExpenses({ tFr, tTo, rname, init: 0 });
	}
}

const createTr = () => {
	let tr = '';
	const { st } = filters();

	payData.forEach(d => {
		const stationFiltered = st ? d.payments.filter(p => p.st === st) : d.payments;
		const payDataFiltered = filterBySource(stationFiltered);
		const payAmo = formatNumber(payDataFiltered?.reduce((a, b) => a + Number(b.kiasi), 0)) || 0,
			recCount = payDataFiltered?.length || 0,
			approval = payDataFiltered?.filter(p => !p.admin_approval).length || 0;
		tr += `<tr data-report=${d.id} class="smallFont cursor-pointer moreDetails" >
					<td><a type="button" data-report=${d.id} class="moreDetails bluePrint" >${d.rname}</a></td>
					<td>${recCount}</td>
					<td>${payAmo}</td>
					<td>
						<a type="button" class="moreDetails" data-report=${d.id}>
						  <span class="badge badge-${approval > 0 ? 'danger' : 'light'}">${approval}</span> Recs
						</a>
					</td>
				</tr>`;
	});

	$('#paymentSummaryBody').html(tr);
};

$('body').on('click', '.moreDetails', function () {
	const val = $(this).data('report');
	const data = payData.filter(d => d.id === val)[0];
	useData = data;
	renderPaymentDetails(data);
});

$('#backToSummary').on('click', function () {
	$('#paymentDetails').hide();
	$('#paymentSummary').show();
	$('#approveAllPayments').prop('disabled', true);
	$('#unapprovedCount').text('0');
	$('#selectAllPayments').prop('checked', false);
});

const renderPaymentDetails = d => {
	const { payments, rname } = d,
		modalTitle = lang('Matumizi - ', 'Shift Expenses - ') + `<span class="bluePrint">${rname}</span>`;
	let tr = '';

	const { st } = filters();
	const stationFiltered = st ? payments.filter(p => p.st === st) : payments;
	const filteredPayments = filterBySource(stationFiltered);

	const approvedCount = filteredPayments?.filter(p => p.admin_approval).length || 0;
	let count = 0;
	filteredPayments.forEach(p => {
		count += 1;
		const canDelete = !p.admin_approval && !!p.akaunti_id && !p.fromShift_id;
		const pumpAttendant = p.payment_source === 'pump_attendant' ? `${p.pump_attendant_fname || ''} ${p.pump_attendant_lname || ''}`.trim() || '-' : '-';
		tr += `<tr class="smallFont cursor-pointer">
					${isAdmin ? `<td class="text-center cursor-pointer">
						<input type="checkbox" class="selectPayment cursor-pointer" ${p.admin_approval ? 'checked disabled' : ''} data-id="${p.id}">
					</td>` : ''}
					<td>${count}</td>
					<td>${moment(p.tarehe).format('DD/MM/YYYY HH:mm')}</td>
					<td>${p.stN || ''}</td>
					<td class="text-capitalize">${p.BFname || ''} ${p.BLname || ''}</td>
					<td>${p.expN || ''}${p.salary_advance ? ` (${lang('Malipo ya awali', 'Salary Advance')})` : ''}</td>
					<td>${paymentSourceLabel(p)}</td>
					<td class="text-capitalize">${pumpAttendant}</td>
					<td>${p.account_name || '-'}</td>
					<td>${p.maelezo || p.kabidhiwa || '-'}</td>
					<td>${formatNumber(p.kiasi) || 0}</td>
					<td>
					  <span>${p.admin_approval ? lang('Imethibitishwa', 'Approved') : lang('Haijathibitishwa', 'Unapproved')}</span>
					  ${canDelete && isAdmin ? `<button type="button" class="btn btn-sm btn-danger deletePayment" data-id="${p.id}">Delete</button>` : ''}
					</td>
				</tr>`;
	});

	const totalAmount = filteredPayments?.reduce((a, b) => a + Number(b.kiasi), 0) || 0;
	tr += `<tr class="smallFont font-weight-bold">
				<td colspan="${isAdmin ? 10 : 9}">Total</td>
				<td>${formatNumber(totalAmount)}</td>
				<td>${approvedCount}/${filteredPayments?.length || 0} ${lang('uhakiki', 'Approval')}</td>
			</tr>`;

	$('#paymentDetailsTitle').html(modalTitle);
	$('#paymentsBody').html(tr);
	$('#paymentSummary').hide();
	$('#paymentDetails').show();
};

$('body').on('click', '.deletePayment', function () {
	payId = Number($(this).data('id')) || 0;
	$('#confirmDeleteModal').modal('show');
});

$('body').on('click', '#confirmDeletePayment', function () {
	$('#confirmDeleteModal').modal('hide');
	$('#loadMe').modal('show');
	const data = {
		'expense_ids[]': [payId],
		expense_ids: JSON.stringify([payId])
	};
	const req = POSTREQUEST({ data, url: '/salepurchase/deleteShiftExpenses' });
	req.then(res => {
		$('#loadMe').modal('hide');
		hideLoading();
		if (res.success) {
			toastr.success(lang('Rekodi imefutwa kwa mafanikio', 'Expense deleted successfully'), lang('Imekamilika', 'Success'), { timeOut: 2000 });
			sesStorage();
			location.reload();
		} else {
			toastr.error(lang(res.swa, res.eng), lang('Haikufanikiwa', 'Error '), { timeOut: 2000 });
		}
	}).catch(() => {
		hideLoading();
		toastr.error(lang('Tatizo la mtandao, jaribu tena', 'Network error, try again'), lang('Haikufanikiwa', 'Error '), { timeOut: 2000 });
	});
});

$('body').on('change', '.selectPayment, #selectAllPayments', function () {
	const isCheckAll = Number($(this).data('ckeckall')) || 0;
	if (isCheckAll) {
		const isChecked = $(this).is(':checked');
		$('.selectPayment').each(function () {
			if (!$(this).is(':disabled')) {
				$(this).prop('checked', isChecked);
			}
		});
	}

	const selectedPayments = $('.selectPayment:checked').filter(function () {
		return !$(this).is(':disabled');
	}).map(function () {
		return $(this).data('id');
	}).get();

	$('#approveAllPayments').prop('disabled', selectedPayments.length === 0);
	$('#unapprovedCount').text(selectedPayments.length);
});

$('#confirmApprovePayments').on('click', function () {
	const selectedPayments = $('.selectPayment:checked').filter(function () {
		return !$(this).is(':disabled');
	}).map(function () {
		return $(this).data('id');
	}).get();

	if (selectedPayments.length === 0) {
		toastr.info(lang('Hakuna matumizi yaliyoteuliwa', 'No expenses selected'), lang('Taarifa', 'info '), { timeOut: 2000 });
		return;
	}

	$('#confirmApprovalModal').modal('hide');
	$('#loadMe').modal('show');
	const data = {
		expense: 1,
		payment_ids: JSON.stringify(selectedPayments)
	};
	const req = POSTREQUEST({ data, url: '/salepurchase/approveShiftCustomerMobilePayments' });
	req.then(res => {
		$('#loadMe').modal('hide');
		hideLoading();
		if (res.success) {
			toastr.success(lang('Matumizi yamehakikiwa kwa mafanikio', 'Expenses approved successfully'), lang('Imekamilika', 'Success'), { timeOut: 2000 });
			sesStorage();
			location.reload();
		} else {
			toastr.error(lang(res.swa, res.eng), lang('Haikufanikiwa', 'Error '), { timeOut: 2000 });
		}
	}).catch(() => {
		hideLoading();
		toastr.error(lang('Tatizo la mtandao, jaribu tena', 'Network error, try again'), lang('Haikufanikiwa', 'Error '), { timeOut: 2000 });
	});
});


$('#stationFilter, #paymentSourceFilter').on('change', function () {
	createTr();
	if ($('#paymentDetails').is(':visible') && useData.payments) {
		renderPaymentDetails(useData);
	}
});

$('#customDateSubmit').on('click', function () {
	const tFr = moment($('#startDate').val()).format(),
		tTo = moment($('#endDate').val()).format(),
		rname = $('#durationName').val();

	if (!rname) {
		redborder('#durationName');
		toastr.error(lang('Tafadhali weka jina la muda', 'Please enter duration name'), lang('Haikufanikiwa', 'Error '), { timeOut: 2000 });
		return;
	}

	if (!tFr || !tTo) {
		toastr.error(lang('Tafadhali chagua tarehe zote mbili', 'Please select both dates'), lang('Haikufanikiwa', 'Error '), { timeOut: 2000 });
		return;
	}
	$('#durationModal').modal('hide');
	createArray(rname, tFr, tTo);
});

function sesStorage() {
	const allExpenseIds = payData.flatMap(item => item.payments.map(p => p.id));
	const exp_Ids = [...new Set(allExpenseIds)];
	const simplifiedExpenseObjects = payData.map(({ rname, tFr, tTo }) => ({
		rname,
		tFr,
		tTo
	}));

	sessionStorage.setItem('exp_Ids', JSON.stringify(exp_Ids));
	sessionStorage.setItem('simplifiedExpenseObjects', JSON.stringify(simplifiedExpenseObjects));
}

$('#printPayments').click(function () {
	const { tFr, tTo } = useData;
	const ddiff = moment(tTo).diff(moment(tFr), 'days');
	const repoDura = ddiff > 1 ? `${moment(tFr).format('DD/MM/YYYY')} - ${moment(tTo).format('DD/MM/YYYY')}` : moment(tTo).format('DD/MM/YYYY');
	const heading = `<h2>${lang('Matumizi:', 'Shift Expenses:')} ${repoDura}</h2>`;
	const userN = $('#user_userName').val();
	const { st } = filters();
	const Kituo = st ? $('#stationFilter').find('option:selected').data('stxn') : lang('Vituo Vyote', 'All Stations');
	const statementDetails = `<div class="row my-3">
							<div class="col-6 row">
								<div class="col-5">${lang('Kituo', 'Station')}:</div>
								<div class="col-7">${Kituo}</div>
								<div class="col-5">${lang('Imetolewa', 'Issued on')}:</div>
								<div class="col-7">${moment().format('DD/MM/YYYY HH:mm')}</div>
								<div class="col-5">${lang('Imetolewa na', 'Issued by')}:</div>
								<div class="col-7 text-capitalize">${userN}</div>
							</div>
						</div>`;

	const theReportData = document.getElementById('paymentsTable').innerHTML;
	const reportData = heading + statementDetails + theReportData;
	const printWindow = window.open('', '', 'height=600,width=1000');
	printWindow.document.write(company_header);
	printWindow.document.write(`${reportData}`);
	printWindow.document.write('</body></html>');
	printWindow.document.close();
	printWindow.focus();
});
