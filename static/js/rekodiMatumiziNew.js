function openModal() {
        document.getElementById('expenseType').focus();
    }


      const getExpData = ()=>{
            const data = {data:{},url:'/accounting/getExpData'}
            $('#loadMe').modal('show')
            const sendIt = POSTREQUEST(data)
            sendIt.done(function(response){
                $('#loadMe').modal('hide')
                hideLoading()
                console.log('Exp data response:', response);
                if(response.success){
                    hydrateBackendData(response)
                } else {
                    // alert('Imeshindikana kupakia taarifa za matumizi')
                }
            }).fail(function(){
                $('#loadMe').modal('hide')
                hideLoading()
                // alert('Imeshindikana kupakia taarifa za matumizi')
            })
        }


       $(document).ready(function(){

            getExpData();
        })


    const itemsByCat = {
        supplies: [],
        allowance: [],
        fuel: [],
        mishahara: [],
        bills: [],
        customer_discounts: []
    };

    const staffMembers = [];
    const sourcePumpAttendants = [];
    const paymentAccounts = [];
    const shiftPumps = [];
    const salaryExpenses = [];
    const salaryPayees = [];

    const expenseType = document.getElementById('expenseType');
    const expenseItem = document.getElementById('expenseItem');
    const expenseItemValue = document.getElementById('expenseItemValue');
    const expenseItemWrapper = document.getElementById('expenseItemWrapper');
    const expenseItemList = document.getElementById('expenseItemList');

    const sourceWrapper = document.getElementById('sourceWrapper');
    const paymentSource = document.getElementById('paymentSource');
    const paymentAccountWrapper = document.getElementById('paymentAccountWrapper');
    const paymentAccount = document.getElementById('paymentAccount');
    const sourcePumpAttendantWrapper = document.getElementById('sourcePumpAttendantWrapper');
    const sourcePumpAttendant = document.getElementById('sourcePumpAttendant');
    const sourcePumpAttendantValue = document.getElementById('sourcePumpAttendantValue');

    const fuelFields = document.getElementById('fuelFields');
    const commonFields = document.getElementById('commonFields');
    const commonAmountWrapper = document.getElementById('commonAmountWrapper');
    const mishaharaFields = document.getElementById('mishaharaFields');

    const recipientTypeWrapper = document.getElementById('recipientTypeWrapper');
    const recipientType = document.getElementById('recipientType');
    const staffWrapper = document.getElementById('staffWrapper');
    const staffMember = document.getElementById('staffMember');
    const staffMemberValue = document.getElementById('staffMemberValue');
    const externalWrapper = document.getElementById('externalWrapper');
    const externalTinWrapper = document.getElementById('externalTinWrapper');
    const externalNinWrapper = document.getElementById('externalNinWrapper');
    const customerNameWrapper = document.getElementById('customerNameWrapper');
    const customerName = document.getElementById('customerName');
    const extName = document.getElementById('extName');
    const extTin = document.getElementById('extTin');
    const extNin = document.getElementById('extNin');

    const generalAmount = document.getElementById('generalAmount');
    const dispenser = document.getElementById('dispenser');
    const nozzle = document.getElementById('nozzle');
    const fuelQty = document.getElementById('fuelQty');
    const fuelAmount = document.getElementById('fuelAmount');

    const mishaharaStaff = document.getElementById('mishaharaStaff');
    const mishaharaStaffValue = document.getElementById('mishaharaStaffValue');
    const mishaharaAmount = document.getElementById('mishaharaAmount');
    const salaryAdvanceToggle = document.getElementById('salaryAdvanceToggle');
    const salaryAdvanceDeductionWrapper = document.getElementById('salaryAdvanceDeductionWrapper');
    const salaryAdvanceDeduction = document.getElementById('salaryAdvanceDeduction');
    const salaryAdvanceCompletionPanel = document.getElementById('salaryAdvanceCompletionPanel');
    const salaryAdvanceCompletionDate = document.getElementById('salaryAdvanceCompletionDate');
    const mishaharaPeriodWrapper = document.getElementById('mishaharaPeriodWrapper');
    const mishaharaPeriod = document.getElementById('mishaharaPeriod');
    const salaryLoanPanel = document.getElementById('salaryLoanPanel');
    const salaryDeductionToggle = document.getElementById('salaryDeductionToggle');
    const salaryLoanAmountValue = document.getElementById('salaryLoanAmountValue');
    const salaryPaidLoanValue = document.getElementById('salaryPaidLoanValue');
    const salaryDeductionValue = document.getElementById('salaryDeductionValue');

    const description = document.getElementById('description');
    const addBtn = document.getElementById('addBtn');
    const saveAll = document.getElementById('saveAll');
    const tableBody = document.getElementById('tableBody');
    const allExpensesTotalAmount = document.getElementById('allExpensesTotalAmount');
    const allExpensesCount = document.getElementById('allExpensesCount');
    const expenseForm = document.getElementById('expenseForm');
    const expenseDateTime = document.getElementById('expenseDateTime');

    // Set default value to current local datetime
    (function setDefaultDateTime() {
        if (!expenseDateTime) return;
        const now = new Date();
        const pad = n => String(n).padStart(2, '0');
        const localStr = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
        expenseDateTime.value = localStr;
    })();

    const amountFields = [generalAmount, fuelAmount, mishaharaAmount, salaryAdvanceDeduction].filter(Boolean);

    const expenses = [];

    function dedupeById(list) {
        const map = new Map();
        list.forEach(item => {
            if (!item || item.id === undefined || item.id === null) return;
            map.set(String(item.id), { ...item, id: String(item.id) });
        });
        return Array.from(map.values());
    }

    function setArrayData(target, items) {
        target.length = 0;
        items.forEach(item => target.push(item));
    }

    function populatePaymentAccountsSelect() {
        if (!paymentAccount) return;

        paymentAccount.innerHTML = `<option value="">-- ${lang('Chagua Akaunti','Select Account')} --</option>`;
        paymentAccounts.forEach(acc => {
            const option = document.createElement('option');
            option.value = acc.id;
            const amount = Number(acc.Amount || 0).toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            option.textContent = `${acc.name} (${acc.aina}) - ${amount}`;
            paymentAccount.appendChild(option);
        });
    }

    function populateDispenserOptions() {
        if (!dispenser) return;

        dispenser.innerHTML = `<option value="">-- ${lang('Chagua Dispenser','Select Dispenser')} --</option>`;
        shiftPumps.forEach(pump => {
            const option = document.createElement('option');
            option.value = String(pump.id);
            option.textContent = pump.name;
            dispenser.appendChild(option);
        });

        populateNozzleOptions();
    }

    function populateNozzleOptions() {
        if (!nozzle) return;

        const selectedDispenserId = String(dispenser?.value || '');
        const selectedPump = shiftPumps.find(p => String(p.id) === selectedDispenserId);
        const nozzles = selectedPump?.nozzles || [];

        nozzle.innerHTML = `<option value="">-- ${lang('Chagua Nozzle','Select Nozzle')} --</option>`;
        nozzles.forEach(nzl => {
            const option = document.createElement('option');
            option.value = String(nzl.id);
            option.textContent = `${nzl.name} (${nzl.fuel || '-'})`;
            option.dataset.price = String(nzl.price || 0);
            nozzle.appendChild(option);
        });

        updateFuelAmountFromQty();
    }

    let _fuelCalcLock = false;

    function updateFuelAmountFromQty() {
        if (!fuelQty || !fuelAmount || !nozzle) return;
        if (_fuelCalcLock) return;

        const qty = parseMoneyValue(fuelQty.value);
        const unitPrice = parseFloat(nozzle.options?.[nozzle.selectedIndex]?.dataset?.price || '0');
        const total = qty * unitPrice;

        _fuelCalcLock = true;
        if (qty > 0 && unitPrice > 0) {
            fuelAmount.value = total.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        } else if (!qty) {
            fuelAmount.value = '';
        }
        _fuelCalcLock = false;
    }

    function updateFuelQtyFromAmount() {
        if (!fuelQty || !fuelAmount || !nozzle) return;
        if (_fuelCalcLock) return;

        const amount = parseMoneyValue(fuelAmount.value);
        const unitPrice = parseFloat(nozzle.options?.[nozzle.selectedIndex]?.dataset?.price || '0');

        _fuelCalcLock = true;
        if (amount > 0 && unitPrice > 0) {
            const qty = amount / unitPrice;
            fuelQty.value = parseFloat(qty.toFixed(3));
        } else if (!amount) {
            fuelQty.value = '';
        }
        _fuelCalcLock = false;
    }

    function hydrateBackendData(response) {
        const backendExpenses = Array.isArray(response.expenses) ? response.expenses : [];
        const backendAccounts = Array.isArray(response.payment_accounts) ? response.payment_accounts : [];
        const backendPumps = Array.isArray(response.shift_pumps) ? response.shift_pumps : [];
        const backendAttendants = Array.isArray(response.attendants) ? response.attendants : [];
        const backendStaffPosho = Array.isArray(response.staff_posho) ? response.staff_posho : [];
        const backendSalary = Array.isArray(response.salary_expenses) ? response.salary_expenses : [];

        const supplies = [];
        const allowance = [];
        const fuel = [];
        const bills = [];
        const customerDiscounts = [];

        backendExpenses.forEach(exp => {
            const item = {
                id: String(exp.id),
                name: exp.name,
                mafuta: !!exp.mafuta,
                bili: !!exp.bili,
                posho: !!exp.posho,
                manunuzi: !!exp.manunuzi,
                discount: !!exp.discount,
                amount: exp.amount,
                depends: exp.depends
            };

            if (exp.mafuta) {fuel.push(item);}
            if (exp.posho) {allowance.push(item);}
            if (exp.bili) {bills.push(item);}
            if (exp.discount) {customerDiscounts.push(item);}
            if (exp.manunuzi) {supplies.push(item);}
            if (!exp.mafuta && !exp.posho && !exp.bili && !exp.manunuzi && !exp.discount) {supplies.push(item);}
        });

        setArrayData(itemsByCat.supplies, dedupeById(supplies));
        setArrayData(itemsByCat.allowance, dedupeById(allowance));
        setArrayData(itemsByCat.fuel, dedupeById(fuel));
        setArrayData(itemsByCat.bills, dedupeById(bills));
        setArrayData(itemsByCat.customer_discounts, dedupeById(customerDiscounts));

        const staffFromPosho = backendStaffPosho.map(st => ({
            id: String(st.user),
            name: `${st.staff_fname || ''} ${st.staff_lname || ''}`.trim()
        }));

        const staffFromSalary = backendSalary
            .filter(s => s.staff_id)
            .map(s => ({ id: String(s.staff_id), name: s.payee_name }));

        const salaryPayeeData = backendSalary
            .filter(s => s.payee_name)
            .map(s => ({
                id: String(s.staff_id || s.id),
                name: String(s.payee_name),
                kopesheka: !!s.kopesheka
            }));

        setArrayData(staffMembers, dedupeById([...staffFromPosho, ...staffFromSalary]));
        setArrayData(sourcePumpAttendants, dedupeById(backendAttendants.map(att => ({
            id: String(att.id),
            name: att.name
        }))));
        setArrayData(paymentAccounts, backendAccounts.map(acc => ({
            id: String(acc.id),
            name: acc.name,
            Amount: acc.Amount,
            aina: acc.aina
        })));
        setArrayData(shiftPumps, backendPumps.map(pmp => ({
            id: String(pmp.id),
            name: pmp.name,
            shift: pmp.shift,
            nozzles: Array.isArray(pmp.nozzles)
                ? pmp.nozzles.map(nzl => ({
                    id: String(nzl.id),
                    name: nzl.name,
                    fuel: nzl.fuel,
                    price: Number(nzl.price || 0)
                }))
                : []
        })));
        setArrayData(salaryExpenses, backendSalary);
        setArrayData(salaryPayees, dedupeById(salaryPayeeData));

        populatePaymentAccountsSelect();
        populateDispenserOptions();
        updateExpenseTypeFields();
        refreshAllSelectVisualState();
    }

    function normalizeMoneyValue(value) {
        return String(value || '').replace(/,/g, '').trim();
    }

    function parseMoneyValue(value) {
        const parsed = parseFloat(normalizeMoneyValue(value));
        return Number.isFinite(parsed) ? parsed : 0;
    }

    function formatMoneyWithCommas(value) {
        const normalized = normalizeMoneyValue(value);
        if (!normalized) return '';

        const negative = normalized.startsWith('-');
        const clean = negative ? normalized.slice(1) : normalized;
        const [intPartRaw, decPartRaw] = clean.split('.');
        const intPart = (intPartRaw || '0').replace(/\D/g, '');
        const decPart = (decPartRaw || '').replace(/\D/g, '');

        const groupedInt = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        const withSign = `${negative ? '-' : ''}${groupedInt}`;

        return decPartRaw !== undefined ? `${withSign}.${decPart}` : withSign;
    }

    function attachAmountFormatting() {
        amountFields.forEach(field => {
            if (field.type === 'number') {
                field.type = 'text';
            }
            field.setAttribute('inputmode', 'decimal');
            field.classList.add('amount-field');

            field.addEventListener('input', () => {
                const formatted = formatMoneyWithCommas(field.value);
                field.value = formatted;
            });

            field.addEventListener('blur', () => {
                const amount = parseMoneyValue(field.value);
                field.value = amount > 0
                    ? amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                    : '';
            });
        });
    }

    function updateSelectVisualState(selectEl) {
        if (!selectEl) return;
        selectEl.classList.toggle('selected-field', !!selectEl.value);
    }

    function bindSelectVisualState() {
        expenseForm.querySelectorAll('select').forEach(selectEl => {
            selectEl.addEventListener('change', () => updateSelectVisualState(selectEl));
            updateSelectVisualState(selectEl);
        });
    }

    function refreshAllSelectVisualState() {
        expenseForm.querySelectorAll('select').forEach(updateSelectVisualState);
    }

    function setupAutocomplete(inputEl, listEl, hiddenEl, data, labelKey = 'name', onSelect = null) {
        if (!inputEl || !listEl) return;

        function renderList(filtered) {
            listEl.innerHTML = '';

            if (!filtered.length) {
                listEl.classList.add('hidden');
                return;
            }

            filtered.forEach(item => {
                const div = document.createElement('div');
                div.className = 'autocomplete-item';
                div.textContent = typeof item === 'string' ? item : item[labelKey];
                div.addEventListener('click', () => {
                    const label = typeof item === 'string' ? item : item[labelKey];
                    const value = typeof item === 'string' ? item : (item.id ?? item[labelKey]);

                    inputEl.value = label;
                    if (hiddenEl) hiddenEl.value = value;
                    inputEl.classList.add('selected-value');
                    listEl.classList.add('hidden');

                    if (typeof onSelect === 'function') {
                        onSelect(item);
                    }
                });
                listEl.appendChild(div);
            });

            listEl.classList.remove('hidden');
        }

        inputEl.addEventListener('input', () => {
            const q = inputEl.value.trim().toLowerCase();
            if (hiddenEl) hiddenEl.value = '';
            inputEl.classList.toggle('selected-value', !!inputEl.value.trim());

            if (!q) {
                listEl.classList.add('hidden');
                listEl.innerHTML = '';
                return;
            }

            const filtered = data.filter(item => {
                const text = (typeof item === 'string' ? item : item[labelKey]).toLowerCase();
                return text.includes(q);
            });

            renderList(filtered);
        });

        inputEl.addEventListener('focus', () => {
            const q = inputEl.value.trim().toLowerCase();
            const filtered = data.filter(item => {
                const text = (typeof item === 'string' ? item : item[labelKey]).toLowerCase();
                return !q || text.includes(q);
            });
            renderList(filtered);
        });

        document.addEventListener('click', (e) => {
            if (!listEl.contains(e.target) && e.target !== inputEl) {
                listEl.classList.add('hidden');
            }
        });
    }

    function isTruthyDepends(dependsValue) {
        if (typeof dependsValue === 'boolean') return dependsValue;
        if (typeof dependsValue === 'number') return dependsValue === 1;
        if (typeof dependsValue === 'string') {
            const normalized = dependsValue.trim().toLowerCase();
            return normalized === '1' || normalized === 'true' || normalized === 'yes';
        }
        return false;
    }

    function setFormattedAmount(field, amountValue) {
        if (!field) return;

        const amount = Number(amountValue || 0);
        field.value = amount > 0
            ? amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
            : '';
    }

    function formatMoney(amountValue) {
        return Number(amountValue || 0).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    function getPaidLoanFromSalaryData(salaryData) {
        return Number(
            salaryData?.paid_loan
            ?? salaryData?.paidLoan
            ?? salaryData?.paid_amount
            ?? 0
        );
    }

    function updateSalaryPanelValues(salaryData) {
        if (!salaryData) {
            salaryLoanPanel?.classList.add('hidden');
            if (salaryLoanAmountValue) salaryLoanAmountValue.textContent = formatMoney(0);
            if (salaryPaidLoanValue) salaryPaidLoanValue.textContent = formatMoney(0);
            if (salaryDeductionValue) salaryDeductionValue.textContent = formatMoney(0);
            return;
        }

        const hasLoan = !!salaryData.has_loan;
        const loanAmount = Number(salaryData.loan_amount || 0);
        const paidLoan = getPaidLoanFromSalaryData(salaryData);
        const deduction = Number(salaryData.salary_deduction || 0);

        if (salaryLoanAmountValue) salaryLoanAmountValue.textContent = formatMoney(loanAmount);
        if (salaryPaidLoanValue) salaryPaidLoanValue.textContent = formatMoney(paidLoan);
        if (salaryDeductionValue) salaryDeductionValue.textContent = formatMoney(deduction);

        salaryLoanPanel?.classList.toggle('hidden', !hasLoan);
    }

    function calculateSalaryAmountByToggle(salaryData) {
        if (salaryAdvanceToggle?.checked) {
            return;
        }

        if (!salaryData) {
            setFormattedAmount(mishaharaAmount, 0);
            return;
        }

        const baseAmount = Number(salaryData.payee_Amount || 0);
        const deduction = Number(salaryData.salary_deduction || 0);
        const useDeductions = !!salaryDeductionToggle?.checked;
        const shouldDeduct = !!salaryData.has_loan && useDeductions;
        const finalAmount = shouldDeduct ? Math.max(baseAmount - deduction, 0) : baseAmount;

        setFormattedAmount(mishaharaAmount, finalAmount);
    }

    function getEndOfMonth(baseDate) {
        const dt = new Date(baseDate.getFullYear(), baseDate.getMonth() + 1, 0);
        dt.setHours(0, 0, 0, 0);
        return dt;
    }

    function formatDateYmd(dateObj) {
        const pad = n => String(n).padStart(2, '0');
        return `${dateObj.getFullYear()}-${pad(dateObj.getMonth() + 1)}-${pad(dateObj.getDate())}`;
    }

    function getSalaryAdvanceCompletionDate() {
        const loanAmount = parseMoneyValue(mishaharaAmount?.value);
        const monthlyDeduction = parseMoneyValue(salaryAdvanceDeduction?.value);

        if (loanAmount <= 0 || monthlyDeduction <= 0) {
            return null;
        }

        const monthsNeeded = Math.ceil(loanAmount / monthlyDeduction);

        let baseDate = new Date();
        if (expenseDateTime?.value) {
            const parsed = new Date(expenseDateTime.value);
            if (!isNaN(parsed.getTime())) {
                baseDate = parsed;
            }
        }

        const completionMonthBase = new Date(baseDate.getFullYear(), baseDate.getMonth() + Math.max(monthsNeeded - 1, 0), 1);
        return getEndOfMonth(completionMonthBase);
    }

    function updateSalaryAdvanceCompletionPanel() {
        const isAdvance = !!salaryAdvanceToggle?.checked;
        if (!isAdvance) {
            salaryAdvanceCompletionPanel?.classList.add('hidden');
            if (salaryAdvanceCompletionDate) salaryAdvanceCompletionDate.textContent = '-';
            return;
        }

        const completionDate = getSalaryAdvanceCompletionDate();
        salaryAdvanceCompletionPanel?.classList.toggle('hidden', !completionDate);
        if (salaryAdvanceCompletionDate) {
            salaryAdvanceCompletionDate.textContent = completionDate ? formatDateYmd(completionDate) : '-';
        }
    }

    function updateSalaryAdvanceUi() {
        const isAdvance = !!salaryAdvanceToggle?.checked;

        salaryAdvanceDeductionWrapper?.classList.toggle('hidden', !isAdvance);
        mishaharaPeriodWrapper?.classList.toggle('hidden', isAdvance);

        if (isAdvance) {
            if (mishaharaPeriod) {
                mishaharaPeriod.value = '';
                mishaharaPeriod.classList.remove('selected-value');
            }

            salaryLoanPanel?.classList.add('hidden');

            if (mishaharaAmount) {
                mishaharaAmount.value = '';
                mishaharaAmount.classList.remove('selected-value');
            }

            if (salaryDeductionToggle) salaryDeductionToggle.checked = false;
        } else {
            const salaryData = getSelectedSalaryData();
            updateSalaryPanelValues(salaryData);
            calculateSalaryAmountByToggle(salaryData);
        }

        updateSalaryAdvanceCompletionPanel();
    }

    function getSelectedSalaryPayee() {
        const selectedId = String(mishaharaStaffValue.value || '').trim();
        const selectedName = String(mishaharaStaff.value || '').trim().toLowerCase();
        return salaryPayees.find(p => {
            const pid = String(p.id || '').trim();
            const pname = String(p.name || '').trim().toLowerCase();
            return (selectedId && pid === selectedId) || (selectedName && pname === selectedName);
        });
    }

    function updateSalaryAdvanceToggleAvailability() {
        if (!salaryAdvanceToggle) return;

        const payee = getSelectedSalaryPayee();
        const canAdvance = !!payee?.kopesheka;
        const wrapper = document.getElementById('salaryAdvanceToggleWrapper');
        const hint = document.getElementById('salaryAdvanceHint');

        salaryAdvanceToggle.disabled = !canAdvance;

        if (!canAdvance) {
            salaryAdvanceToggle.checked = false;
            updateSalaryAdvanceUi();
        }

        if (wrapper) {
            wrapper.classList.toggle('salary-advance-disabled', !canAdvance);
        }

        // if (hint) {
        //     hint.textContent = canAdvance
        //         ? ''
        //         : lang(
        //             'Staff huyu hawezi kupewa advance ya mshahara',
        //             'This staff member is not eligible for salary advance'
        //           );
        //     hint.style.display = canAdvance ? 'none' : 'block';
        // }
    }

    function applyBillAmountIfFixed(selectedItem) {
        if (expenseType.value !== 'bills' || !selectedItem) return;

        const depends = isTruthyDepends(selectedItem.depends);
        const amount = parseMoneyValue(selectedItem.amount);

        if (!depends && amount > 0) {
            setFormattedAmount(generalAmount, amount);
            generalAmount.classList.add('selected-value');
        }
    }

    function getSelectedExpenseItem() {
        const items = itemsByCat[expenseType.value] || [];
        const byId = String(expenseItemValue.value || '').trim();
        const byName = String(expenseItem.value || '').trim().toLowerCase();

        return items.find(item => {
            const itemId = String(item.id || '').trim();
            const itemName = String(item.name || '').trim().toLowerCase();
            return (byId && itemId === byId) || (byName && itemName === byName);
        });
    }

    function updateSourceSpecificFields() {
        const selectedSource = paymentSource.value;
        paymentAccountWrapper.classList.toggle('hidden', selectedSource !== 'headOffice');
        sourcePumpAttendantWrapper.classList.toggle('hidden', selectedSource !== 'pumpAttendant');
        refreshAllSelectVisualState();
    }

    function updateRecipientFields() {
        const isCustomerDiscount = expenseType.value === 'customer_discounts';

        if (isCustomerDiscount) {
            recipientTypeWrapper?.classList.add('hidden');
            staffWrapper.classList.add('hidden');
            externalWrapper.classList.add('hidden');
            externalTinWrapper.classList.add('hidden');
            externalNinWrapper.classList.add('hidden');
            customerNameWrapper?.classList.remove('hidden');

            staffMember.value = '';
            staffMemberValue.value = '';
            extName.value = '';
            extTin.value = '';
            extNin.value = '';
            refreshAllSelectVisualState();
            return;
        }

        recipientTypeWrapper?.classList.remove('hidden');
        customerNameWrapper?.classList.add('hidden');
        customerName.value = '';

        const isExternal = recipientType.value === 'external';
        staffWrapper.classList.toggle('hidden', isExternal);
        externalWrapper.classList.toggle('hidden', !isExternal);
        externalTinWrapper.classList.toggle('hidden', !isExternal);
        externalNinWrapper.classList.toggle('hidden', !isExternal);
        
        if(isExternal) {
            document.getElementById('extName').value = '';
            document.getElementById('extTin').value = '';
            document.getElementById('extNin').value = '';
        }

        refreshAllSelectVisualState();
    }

    function updateExpenseTypeFields() {
        const val = expenseType.value;
        const items = itemsByCat[val] || [];

        expenseItem.value = '';
        expenseItemValue.value = '';
        expenseItemList.innerHTML = '';
        expenseItem.classList.remove('selected-value');

        setupAutocomplete(
            expenseItem,
            expenseItemList,
            expenseItemValue,
            items,
            'name',
            applyBillAmountIfFixed
        );

        const isFuel = val === 'fuel';
        const isMishahara = val === 'mishahara';
        const isCustomerDiscount = val === 'customer_discounts';
        const isEmpty = val === '';

        fuelFields.classList.toggle('hidden', !isFuel);
        commonFields.classList.toggle('hidden', isMishahara || isEmpty);
        commonAmountWrapper?.classList.toggle('hidden', isFuel);
        mishaharaFields.classList.toggle('hidden', !isMishahara);
        expenseItemWrapper.classList.toggle('hidden', isMishahara || isCustomerDiscount);

        if (isFuel) {
            sourceWrapper.classList.add('hidden');
            paymentSource.value = '';
            paymentAccount.value = '';
            sourcePumpAttendant.value = '';
            sourcePumpAttendantValue.value = '';
        } else {
            sourceWrapper.classList.remove('hidden');
        }

        if (isMishahara) {
            if (salaryDeductionToggle) salaryDeductionToggle.checked = true;
            refreshSelectedSalaryUi();
            updateSalaryAdvanceUi();
        } else {
            salaryLoanPanel?.classList.add('hidden');
            salaryAdvanceCompletionPanel?.classList.add('hidden');
            salaryAdvanceDeductionWrapper?.classList.add('hidden');
            mishaharaPeriodWrapper?.classList.remove('hidden');
            if (salaryAdvanceToggle) {
                salaryAdvanceToggle.checked = false;
                salaryAdvanceToggle.disabled = true;
            }
            if (salaryAdvanceDeduction) salaryAdvanceDeduction.value = '';
            const hint = document.getElementById('salaryAdvanceHint');
            if (hint) hint.style.display = 'none';
            const wrapper = document.getElementById('salaryAdvanceToggleWrapper');
            if (wrapper) wrapper.classList.remove('salary-advance-disabled');
        }

        updateSourceSpecificFields();
        updateRecipientFields();
        refreshAllSelectVisualState();
    }

    function render() {
        tableBody.innerHTML = '';
        let totalAmount = 0;

        expenses.forEach((expense, index) => {
            totalAmount += Number(expense.amount) || 0;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${expense.item}</td>
                <td>${expense.recipient}</td>
                <td>${expense.desc}</td>
                <td>${Number(expense.amount).toLocaleString('en-US')}</td>
                <td><button type="button" class="trash-btn" data-index="${index}">Delete</button></td>
            `;
            tableBody.appendChild(tr);
        });

        if (allExpensesTotalAmount) {
            allExpensesTotalAmount.textContent = totalAmount.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }

        if (allExpensesCount) {
            allExpensesCount.textContent = expenses.length.toLocaleString('en-US');
        }

        saveAll.disabled = expenses.length === 0;
    }

    function getRecycleState() {
        const state = {};
        document.querySelectorAll('.recylebtn.activeRecyle').forEach(btn => {
            const ids = (btn.dataset.targets || '')
                .split(',')
                .map(v => v.trim())
                .filter(Boolean);

            ids.forEach(id => {
                const el = document.getElementById(id);
                if (el) state[id] = el.value;
            });
        });
        return state;
    }

    function restoreRecycleState(state) {
        Object.entries(state).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.value = value;

            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.classList.toggle('selected-value', !!el.value.trim());
            }

            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        });
    }

    function resetNonRecycledFields() {
        expenseForm.reset();

        expenseItemValue.value = '';
        sourcePumpAttendantValue.value = '';
        staffMemberValue.value = '';
        mishaharaStaffValue.value = '';

        expenseItem.classList.remove('selected-value');
        staffMember.classList.remove('selected-value');
        sourcePumpAttendant.classList.remove('selected-value');
        mishaharaStaff.classList.remove('selected-value');
        description.classList.remove('selected-value');
        mishaharaPeriod.classList.remove('selected-value');

        expenseItemList.innerHTML = '';
        document.getElementById('staffMemberList').innerHTML = '';
        document.getElementById('sourcePumpAttendantList').innerHTML = '';
        document.getElementById('mishaharaStaffList').innerHTML = '';

        updateExpenseTypeFields();
    }

    function validateCommonRecipient(isCustomerDiscount = false) {
        if (isCustomerDiscount) {
            if (!customerName.value.trim()) {
                alert('Andika jina la mteja!');
                return null;
            }
            return customerName.value.trim();
        }

        if (recipientType.value === 'staff') {
            if (!staffMember.value.trim()) {
                alert('Chagua staff!');
                return null;
            }

            if (!String(staffMemberValue.value || '').trim()) {
                alert('Tafadhali chagua staff kutoka kwenye orodha ya mapendekezo!');
                return null;
            }

            return staffMember.value.trim();
        }

        if (!extName.value.trim()) {
            alert('Andika jina la mpokeaji!');
            return null;
        }

        if (!extTin.value.trim()) {
            alert('Andika TIN Number!');
            return null;
        }

        return `${extName.value.trim()} | TIN: ${extTin.value.trim()}${extNin.value.trim() ? ' | NIN: ' + extNin.value.trim() : ''}`;
    }

    function getSelectedSalaryData() {
        const selectedId = String(mishaharaStaffValue.value || '').trim();
        const selectedName = String(mishaharaStaff.value || '').trim().toLowerCase();

        return salaryExpenses.find(sal => {
            const salaryId = String(sal.staff_id || sal.id || '').trim();
            const salaryName = String(sal.payee_name || '').trim().toLowerCase();
            return (selectedId && salaryId === selectedId) || (selectedName && salaryName === selectedName);
        });
    }

    function refreshSelectedSalaryUi() {
        const salaryData = getSelectedSalaryData();
        updateSalaryAdvanceToggleAvailability();

        if (salaryAdvanceToggle?.checked) {
            salaryLoanPanel?.classList.add('hidden');
            updateSalaryAdvanceCompletionPanel();
            return;
        }

        updateSalaryPanelValues(salaryData);
        calculateSalaryAmountByToggle(salaryData);
        updateSalaryAdvanceCompletionPanel();
    }

    setupAutocomplete(staffMember, document.getElementById('staffMemberList'), staffMemberValue, staffMembers);
    setupAutocomplete(mishaharaStaff, document.getElementById('mishaharaStaffList'), mishaharaStaffValue, salaryPayees, 'name', refreshSelectedSalaryUi);
    setupAutocomplete(sourcePumpAttendant, document.getElementById('sourcePumpAttendantList'), sourcePumpAttendantValue, sourcePumpAttendants);

    expenseType.addEventListener('change', updateExpenseTypeFields);
    paymentSource.addEventListener('change', updateSourceSpecificFields);
    recipientType.addEventListener('change', updateRecipientFields);
    description.addEventListener('input', () => {
        description.classList.toggle('selected-value', !!description.value.trim());
    });
    mishaharaPeriod.addEventListener('change', () => {
        mishaharaPeriod.classList.toggle('selected-value', !!mishaharaPeriod.value);
    });
    expenseItem.addEventListener('blur', () => applyBillAmountIfFixed(getSelectedExpenseItem()));
    expenseItem.addEventListener('change', () => applyBillAmountIfFixed(getSelectedExpenseItem()));
    mishaharaStaff.addEventListener('blur', refreshSelectedSalaryUi);
    mishaharaStaff.addEventListener('change', refreshSelectedSalaryUi);
    salaryDeductionToggle?.addEventListener('change', refreshSelectedSalaryUi);
    salaryAdvanceToggle?.addEventListener('change', updateSalaryAdvanceUi);
    salaryAdvanceDeduction?.addEventListener('input', updateSalaryAdvanceCompletionPanel);
    mishaharaAmount?.addEventListener('input', updateSalaryAdvanceCompletionPanel);
    expenseDateTime?.addEventListener('change', updateSalaryAdvanceCompletionPanel);
    dispenser.addEventListener('change', populateNozzleOptions);
    nozzle.addEventListener('change', updateFuelAmountFromQty);
    fuelQty.addEventListener('input', updateFuelAmountFromQty);
    fuelAmount.addEventListener('input', updateFuelQtyFromAmount);

    document.querySelectorAll('.recylebtn[data-targets]').forEach(btn => {
        btn.style.cursor = 'pointer';
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            this.classList.toggle('activeRecyle');
        });
    });

    addBtn.addEventListener('click', function () {
        const recycleState = getRecycleState();
        const type = expenseType.value;
        const selectedItem = getSelectedExpenseItem();

        if (!type) {
            alert('Chagua aina ya matumizi!');
            return;
        }

        if (type === 'mishahara') {
            const period = mishaharaPeriod.value;
            const isSalaryAdvance = !!salaryAdvanceToggle?.checked;
            let amount = parseMoneyValue(mishaharaAmount.value);
            const selectedStaff = mishaharaStaff.value.trim();
            const salaryData = getSelectedSalaryData();
            const advanceDeductionAmount = parseMoneyValue(salaryAdvanceDeduction?.value);
            const completionDateObj = getSalaryAdvanceCompletionDate();
            const completionDate = completionDateObj ? formatDateYmd(completionDateObj) : '';

            if (!isSalaryAdvance && salaryData) {
                const baseAmount = Number(salaryData.payee_Amount || 0);
                const deduction = Number(salaryData.salary_deduction || 0);
                const useDeductions = !!salaryDeductionToggle?.checked;
                const shouldDeduct = !!salaryData.has_loan && useDeductions;
                amount = shouldDeduct ? Math.max(baseAmount - deduction, 0) : baseAmount;
            }

            if (!selectedStaff) {
                alert('Chagua staff!');
                return;
            }

            if (!salaryData || !salaryData.id) {
                alert('Mshahara huu haujaunganishwa na kundi la matumizi!');
                return;
            }

            if (!amount || amount <= 0) {
                alert('Weka kiasi sahihi!');
                return;
            }

            if (!isSalaryAdvance && !period) {
                alert('Chagua mwezi/kipindi cha mishahara!');
                return;
            }

            if (isSalaryAdvance && (!advanceDeductionAmount || advanceDeductionAmount <= 0)) {
                alert('Weka kiasi cha makato ya mwisho wa mwezi!');
                return;
            }

            if (!paymentSource.value) {
                alert('Chagua chanzo cha malipo!');
                return;
            }

            let sourceInfo = '';
            const sourceDetails = {};
            if (paymentSource.value === 'headOffice') {
                if (!paymentAccount.value) {
                    alert('Chagua payment account ya Ofisi Kuu!');
                    return;
                }
                const accountName = paymentAccount.options[paymentAccount.selectedIndex]?.textContent || paymentAccount.value;
                sourceInfo = `HO - ${accountName}`;
                sourceDetails.account_id = String(paymentAccount.value);
            } else if (paymentSource.value === 'pumpAttendant') {
                if (!sourcePumpAttendant.value.trim() || !sourcePumpAttendantValue.value) {
                    alert('Chagua pump attendant wa chanzo cha malipo!');
                    return;
                }
                sourceInfo = `Pump Attendant - ${sourcePumpAttendant.value.trim()}`;
                sourceDetails.attendant_id = String(sourcePumpAttendantValue.value);
            }

            expenses.push({
                item: isSalaryAdvance ? `Salary Advance` : `Mishahara - ${period}`,
                recipient: `${selectedStaff}${sourceInfo ? ' | ' + sourceInfo : ''}`,
                desc: description.value.trim() || (
                    isSalaryAdvance
                        ? `Advance Loan | Monthly Deduction: ${advanceDeductionAmount.toLocaleString('en-US')} | Completion: ${completionDate || '-'}`
                        : (salaryData && salaryData.has_loan
                            ? `Mkopo: ${Number(salaryData.loan_amount || 0).toLocaleString('en-US')} | Makato: ${Number(salaryData.salary_deduction || 0).toLocaleString('en-US')}`
                            : '-')
                ),
                amount,
                category: 'mishahara',
                expense_group_id: String(salaryData.id),
                receiver_name: selectedStaff,
                remarks: description.value.trim() || '',
                recipient_type: 'staff',
                staff_id: String(salaryData.staff_id || mishaharaStaffValue.value || ''),
                source_type: paymentSource.value,
                source_details: sourceDetails,
                period: isSalaryAdvance ? '' : period,
                salary_period: isSalaryAdvance ? '' : period,
                is_salary_advance: isSalaryAdvance,
                salary_advance_deduction: advanceDeductionAmount,
                salary_advance_completion_date: completionDate
            });

            render();
            resetNonRecycledFields();
            restoreRecycleState(recycleState);
            return;
        }

        if (type === 'fuel') {
            if (!expenseItem.value.trim() || !selectedItem || !expenseItemValue.value) {
                alert('Chagua jina la tumizi la mafuta!');
                return;
            }

            const recipient = validateCommonRecipient();
            if (!recipient) return;

            const isStaffRecipient = recipientType.value === 'staff';

            if (!dispenser.value || !nozzle.value) {
                alert('Jaza dispenser na nozzle!');
                return;
            }

            const fuelQtyValue = parseMoneyValue(fuelQty.value);
            if (!fuelQtyValue || fuelQtyValue <= 0) {
                alert('Weka lita sahihi!');
                return;
            }

            const fuelAmountValue = parseMoneyValue(fuelAmount.value);
            if (!fuelAmountValue || fuelAmountValue <= 0) {
                alert('Weka kiasi sahihi!');
                return;
            }

            const selectedNozzleLabel = nozzle.options[nozzle.selectedIndex]?.textContent || nozzle.value;
            const selectedDispenserLabel = dispenser.options[dispenser.selectedIndex]?.textContent || dispenser.value;

            expenses.push({
                item: `Fuel - ${selectedNozzleLabel}`,
                recipient: `${recipient} | Dispenser: ${selectedDispenserLabel}`,
                desc: `Qty: ${fuelQty.value} L${description.value.trim() ? ' | ' + description.value.trim() : ''}`,
                amount: fuelAmountValue,
                category: 'fuel',
                expense_group_id: String(selectedItem.id),
                receiver_name: isStaffRecipient ? staffMember.value.trim() : extName.value.trim(),
                remarks: description.value.trim() || '',
                recipient_type: recipientType.value,
                staff_id: isStaffRecipient ? String(staffMemberValue.value || '') : '',
                tin_number: isStaffRecipient ? '' : extTin.value.trim(),
                nin_number: isStaffRecipient ? '' : extNin.value.trim(),
                source_type: 'fuelPump',
                source_details: {
                    dispenser_id: String(dispenser.value),
                    nozzle_id: String(nozzle.value),
                    quantity_litres: fuelQtyValue
                }
            });

            render();
            resetNonRecycledFields();
            restoreRecycleState(recycleState);
            return;
        }

        if (!expenseItem.value.trim()) {
            if (type !== 'customer_discounts') {
                alert('Chagua jina la tumizi!');
                return;
            }
        }

        if (type !== 'customer_discounts' && (!selectedItem || !expenseItemValue.value)) {
            alert('Tafadhali chagua tumizi kutoka kwenye orodha!');
            return;
        }

        if (!paymentSource.value) {
            alert('Chagua chanzo cha malipo!');
            return;
        }

        let sourceInfo = '';
        const sourceDetails = {};
        if (paymentSource.value === 'headOffice') {
            if (!paymentAccount.value) {
                alert('Chagua payment account!');
                return;
            }
            const accountName = paymentAccount.options[paymentAccount.selectedIndex]?.textContent || paymentAccount.value;
            sourceInfo = `HO - ${accountName}`;
            sourceDetails.account_id = String(paymentAccount.value);
        } else if (paymentSource.value === 'pumpAttendant') {
            if (!sourcePumpAttendant.value.trim() || !sourcePumpAttendantValue.value) {
                alert('Chagua pump attendant!');
                return;
            }
            sourceInfo = `Pump Attendant - ${sourcePumpAttendant.value.trim()}`;
            sourceDetails.attendant_id = String(sourcePumpAttendantValue.value);
        }

        const isCustomerDiscount = type === 'customer_discounts';
        const recipient = validateCommonRecipient(isCustomerDiscount);
        if (!recipient) return;

        const isStaffRecipient = !isCustomerDiscount && recipientType.value === 'staff';

        const generalAmountValue = parseMoneyValue(generalAmount.value);
        if (!generalAmountValue || generalAmountValue <= 0) {
            alert('Weka kiasi sahihi!');
            return;
        }

        expenses.push({
            item: type === 'customer_discounts' ? 'Discount' : expenseItem.value.trim(),
            recipient: `${recipient} | ${sourceInfo}`,
            desc: description.value.trim() || '-',
            amount: generalAmountValue,
            category: type,
            expense_group_id: selectedItem?.id ? String(selectedItem.id) : '',
            receiver_name: isCustomerDiscount ? customerName.value.trim() : (isStaffRecipient ? staffMember.value.trim() : extName.value.trim()),
            remarks: description.value.trim() || '',
            recipient_type: isCustomerDiscount ? 'customer' : recipientType.value,
            staff_id: isStaffRecipient ? String(staffMemberValue.value || '') : '',
            tin_number: isCustomerDiscount || isStaffRecipient ? '' : extTin.value.trim(),
            nin_number: isCustomerDiscount || isStaffRecipient ? '' : extNin.value.trim(),
            customer_name: isCustomerDiscount ? customerName.value.trim() : '',
            source_type: paymentSource.value,
            source_details: sourceDetails
        });

        render();
        resetNonRecycledFields();
        restoreRecycleState(recycleState);
    });

    tableBody.addEventListener('click', function (e) {
        const btn = e.target.closest('.trash-btn');
        if (!btn) return;

        const index = Number(btn.dataset.index);
        expenses.splice(index, 1);
        render();
    });

    expenseForm.addEventListener('submit', function (e) {
        e.preventDefault();

        if (!expenses.length) {
            alert('Hakuna data ya kuhifadhi!');
            return;
        }

        // Build ISO string from the datetime-local input
        let expDateISO = new Date().toISOString();
        if (expenseDateTime && expenseDateTime.value) {
            const dt = new Date(expenseDateTime.value);
            if (!isNaN(dt.getTime())) expDateISO = dt.toISOString();
        }

        const toSend = {
            data: {
                expDate: expDateISO,
                expenses_json: JSON.stringify(expenses)
            },
            url: '/accounting/addExpense'
        };

        $('#loadMe').modal('show');
        const sendIt = POSTREQUEST(toSend);
        sendIt.then((res) => {
            $('#loadMe').modal('hide');
            hideLoading();
            const msg = lang(res.message_swa || 'Imehifadhiwa', res.message_eng || 'Saved successfully');
            if (res.success) {
                toastr.success(msg, lang('Imekamilika', 'Success'), { timeOut: 2000 });
                location.reload();
            } else {
                toastr.error(msg, lang('Hitilafu', 'Error'), { timeOut: 3000 });
            }
        }).catch(() => {
            $('#loadMe').modal('hide');
            hideLoading();
            toastr.error(lang('Imeshindikana kuhifadhi matumizi', 'Failed to save expenses'), lang('Hitilafu', 'Error'), { timeOut: 3000 });
        });
    });

    updateExpenseTypeFields();
    updateSourceSpecificFields();
    updateRecipientFields();
    bindSelectVisualState();
    attachAmountFormatting();
    render();