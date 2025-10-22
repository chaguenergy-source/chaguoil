  let rowCount = 0;
        let currentSource = '', SELPUMPS = [];
        const PRICE_PER_LITRE_SIMULATED = 3200; 
        
        // Kufuatilia dropdown iliyo wazi sasa.
        let activeDropdown = null; 

        // Global state for recycle settings (false = OFF, true = ON)
        let recycleSettings = {
            expenseGroup: false,
            paymentAccount: false,
            pumpAttendant: false
        };

 // --- SIMULATED DATA ---
        let EXPENSE_GROUPS = [
            { id: 'OFS', name: 'Office Supplies', type: 'CASH' },
            { id: 'RMN', name: 'Repairs & Maintenance', type: 'CASH' },
            { id: 'STF', name: 'Staff Welfare', type: 'CASH' },
            { id: 'UTL', name: 'Utilities (Electricity/Water)', type: 'CASH' },
            { id: 'VEH', name: 'Vehicle Maintenance', type: 'FUEL' }, 
            { id: 'SFT', name: 'Software Licences', type: 'CASH' },
            { id: 'MKG', name: 'Marketing & Promotions', type: 'CASH' },
            { id: 'HRD', name: 'Hardware Repair', type: 'CASH' }
        ];

        var SOURCE_TYPES = [
            { id: 'payment', name: `1. ${lang("Akaunti za Malipo","Payments Account")} (Bank/Cash)` } ,
            { id: 'attendant', name: `2. ${lang("Mhusika wa Pampu","Pump Attendant Cash")}` },
            { id: 'fuel', name: `3. ${lang("Mafuta/ Lita ya Kuchota (Matumizi ya Ofisi)","Fuel/Litre Draw (Office Use)")}` }
        ];

        var PAYMENT_ACCOUNTS = [
            { id: 'CASH_SAFE', name: 'Cash Account (Safe/Tellers)' },
            { id: 'BANK_EQUITY', name: 'Equity Bank - Main Ops' },
            { id: 'BANK_CRDB', name: 'CRDB Bank - Operating' },
            { id: 'BANK_NMB', name: 'NMB Bank - Reserve' },
            { id: 'MPESA_HQ', name: 'M-Pesa HQ Float' },
            { id: 'TTB_BANK', name: 'Tanzania Trust Bank' }
        ];

        var ATTENDANTS = [
            { id: 'AT1', name: 'Jane Doe','shift':10 },
            { id: 'AT2', name: 'John Smith','shift':11 },
        ];

        var PUMPS = [
            { id: 'P1',shift:10, name: 'Pump 1', nozzles: [
                { id: 'N1A', name: 'N1A (Petrol)', price: 3200 },
                { id: 'N1B', name: 'N1B (Diesel)', price: 3000 }
            ]},
            { id: 'P2',shift:10, name: 'Pump 2', nozzles: [
                { id: 'N2A', name: 'N2A (Petrol)', price: 3250 },
                { id: 'N2B', name: 'N2B (Kerosene)', price: 2800 }
            ]},
            { id: 'P2',shift:11, name: 'Pump 2', nozzles: [
                { id: 'N2A', name: 'N2A (Petrol)', price: 3250 },
                { id: 'N2B', name: 'N2B (Kerosene)', price: 2800 }
            ]},
            { id: 'P2',shift:12, name: 'Pump 2', nozzles: [
                { id: 'N2A', name: 'N2A (Petrol)', price: 3250 },
                { id: 'N2B', name: 'N2B (Kerosene)', price: 2800 }
            ]}
        ];


  const getExpData = ()=>{
            const data = {data:{},url:'/accounting/getExpData'}
            $('#loadMe').modal('show')
            const sendIt = POSTREQUEST(data)
            sendIt.done(function(response){
                $('#loadMe').modal('hide')
                hideLoading()
              
                if(response.success){

                    EXPENSE_GROUPS = response.expenses
                    // SOURCE_TYPES = response.source_types
                    PAYMENT_ACCOUNTS = response.payment_accounts
                    ATTENDANTS = response.attendants
                    PUMPS = response.shift_pumps
                    SELPUMPS = response.shift_pumps
                   readData()
                 
                    // Process the successful response
                } else {
                    // Handle errors
                }
            })
        }


       $(document).ready(function(){

            getExpData();
        })

        // --- COLOR FEEDBACK LOGIC ---
        
        /**
         * Changes the text color of a standard <select> element to blue if a valid option is chosen.
         * @param {HTMLSelectElement} element - The select element to check.
         */
        function handleSelectColorChange(element) {
           
            if (element.value && element.value !== '') {
                element.classList.add('selected-text');
            
            } else {
                element.classList.remove('selected-text');
            }
        }
        
        // --- CORE FUNCTION FOR HIDING DROPDOWN (MOVED TO GLOBAL SCOPE) ---
        
        /**
         * Hides the currently active dropdown list attached to the body.
         */
        function hideActiveDropdown() {
            if (activeDropdown) {
                activeDropdown.classList.add('hidden');
                activeDropdown = null;
            }
        }
        
        // --- SEARCHABLE SELECT CORE LOGIC: REVISED FOR OVERFLOW FIX ---

        function createSearchableSelectHTML(id, name, placeholder, options, recycleField, extraButtons = '', classes='') {
            const isRecycleOn = recycleSettings[recycleField] ? 'btn-warning' : 'btn-secondary';
            const recycleTitle = recycleSettings[recycleField] 
                ? 'Recycling ON: Next rows will copy last value.' 
                : 'Recycling OFF: Click to copy last value to next rows.';
            
            let recycleButtonHtml = '';
            if (recycleField) {
                recycleButtonHtml = `
                    <button type="button" class="btn btn-sm ms-1 recycle-btn recycle-${recycleField}" onclick="toggleRecycle('${recycleField}', event)" title="${recycleTitle}">
                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.205 13m0 0l2.12-2.12M20 20v-5h-.581m0 0l-2.12 2.12M20.595 13A8.001 8.001 0 013.404 11"></path></svg>
                    </button>
                `;
            }

            // Options List is NOT INCLUDED here. It will be created once and attached to <body>.
            // We just need the input and hidden field wrapper.

            return `
                <div class="searchable-select-wrapper d-flex align-items-center" id="wrapper-${id}">
                    <div class="searchable-select-container flex-grow-1" id="container-${id}">
                        <input type="text" 
                               id="searchInput-${id}" 
                               class="form-control form-control-sm search-input ${classes}" 
                               placeholder="${placeholder}" 
                               autocomplete="off" 
                               data-options-id="list-${id}"
            
                               required>
                        <input type="hidden" 
                               name="${name}" 
                               id="hiddenValue-${id}" 
                               value="">
                    </div>
                    ${extraButtons}
                    ${recycleButtonHtml}
                </div>
            `;
        }
        
        /**
         * Creates the reusable dropdown list element and appends it to the body.
         */
        function createDropdownList(id, options) {
            const list = document.createElement('div');
            list.id = `list-${id}`;
            list.className = 'options-list-dropdown hidden';

            const optionsHtml = options?.map(opt => 
                `<div class="searchable-option" data-value="${opt.id}" data-text="${opt.name}" data-type="${opt.type || ''}">
                    ${opt.name}
                </div>`
            ).join('');

            list.innerHTML = optionsHtml;
            document.body.appendChild(list);
            return list;
        }

        /**
         * Attaches listeners for searchable fields, including color feedback and overflow fix.
         * The fix: Added event.stopPropagation() to the list click listener.
         */
        function attachSearchableSelectListeners(id, optionsData) {
            const input = document.getElementById(`searchInput-${id}`);
            const hiddenInput = document.getElementById(`hiddenValue-${id}`);
            
            // 1. Create and attach the list to the body if it doesn't exist
            let list = document.getElementById(`list-${id}`);
            if (!list) {
                list = createDropdownList(id, optionsData);
            }

            if (!input) return;

            // --- Function to position the dropdown ---
            function positionDropdown() {
                if (input && list) {
                    const rect = input.getBoundingClientRect();
                    list.style.width = `${rect.width}px`;
                    list.style.top = `${rect.bottom + window.scrollY}px`;
                    list.style.left = `${rect.left + window.scrollX}px`;
                }
            }
            
            // --- Filter logic on input ---
            input.addEventListener('input', () => {
                const filter = input.value.toLowerCase();
                let matchedCount = 0;
                
                list.querySelectorAll('.searchable-option').forEach(option => {
                    const text = option.getAttribute('data-text').toLowerCase();
                    if (text.includes(filter)) {
                        option.classList.remove('hidden');
                        matchedCount++;
                    } else {
                        option.classList.add('hidden');
                    }
                });
                
                hideActiveDropdown(); // Ficha mengine kwanza
                if (matchedCount > 0) {
                    positionDropdown();
                    list.classList.remove('hidden');
                    activeDropdown = list;
                }
                
                // Clear hidden value and reset color if the text input changes, forcing re-selection
                if (input.value !== hiddenInput.getAttribute('data-display-text')) {
                    hiddenInput.value = '';
                    input.classList.remove('selected-text'); 
                }
            });

            // --- Show all options on focus ---
            input.addEventListener('focus', () => {
                // Ficha dropdown zote kwanza
                hideActiveDropdown(); 

                // Onyesha hii tu
                list.classList.remove('hidden');
                activeDropdown = list;
                positionDropdown();

                // Fanya input ionyeshe rangi ya selected text kama tayari ina value
                if (hiddenInput.value) {
                    input.classList.add('selected-text');
                } else {
                    input.classList.remove('selected-text');
                }
                
                list.querySelectorAll('.searchable-option').forEach(option => {
                    option.classList.remove('hidden');
                });
            });
            
            // --- Selection logic (Event Delegation on the list element) ---
            list.addEventListener('click', (event) => {
                const option = event.target.closest('.searchable-option');
                if (option) {
                    const value = option.getAttribute('data-value');
                    const text = option.getAttribute('data-text');

                    // Set hidden value for form submission
                    hiddenInput.value = value;
                    hiddenInput.setAttribute('data-display-text', text); 

                    // Update visible input text
                    input.value = text;
                    if(input.classList.contains('pumpAttendants') && currentSource === 'fuel' ){setPumps(input);}

                    // Apply blue color to show selection confirmation
                    input.classList.add('selected-text'); 

                    // Hide the list
                    hideActiveDropdown(); 
                    
                    // === MAREKEBISHO MUHIMU: Zuia click isisambae hadi kwenye document click handler ===
                    event.stopPropagation(); 
                }
            });
            
            // Add click listener to the input for immediate positioning
            input.addEventListener('click', (e) => {
                e.stopPropagation(); // Zuia kusambaa kwa click
                positionDropdown();
            });
        }
        
        // --- Hide list when clicking outside (Global Listener) ---
        document.addEventListener('click', (event) => {
            if (activeDropdown) {
                const listId = activeDropdown.id;
                const baseId = listId.replace('list-', ''); 
                
                const input = document.getElementById(`searchInput-${baseId}`);
                const hiddenInput = document.getElementById(`hiddenValue-${baseId}`);

                if (input && hiddenInput && !input.contains(event.target) && !activeDropdown.contains(event.target)) {
                    
                    if (hiddenInput.value) {
                        // Restore the selected text and color if a value is set
                         input.value = hiddenInput.getAttribute('data-display-text');
                         input.classList.add('selected-text'); // Maintain blue color
                    } else {
                        // Clear input if no value was set
                        input.value = '';
                        input.classList.remove('selected-text');
                    }

                    activeDropdown.classList.add('hidden');
                    activeDropdown = null;
                }
            }
        });
        
        // Handle window resize/scroll to reposition active dropdown
        window.addEventListener('resize', () => {
             if (activeDropdown) {
                const input = document.getElementById(activeDropdown.id.replace('list-', 'searchInput-'));
                if (input) {
                    const rect = input.getBoundingClientRect();
                    activeDropdown.style.width = `${rect.width}px`;
                    activeDropdown.style.top = `${rect.bottom + window.scrollY}px`;
                    activeDropdown.style.left = `${rect.left + window.scrollX}px`;
                } else {
                    activeDropdown.classList.add('hidden');
                    activeDropdown = null;
                }
            }
        });
        
        window.addEventListener('scroll', () => {
             if (activeDropdown) {
                const input = document.getElementById(activeDropdown.id.replace('list-', 'searchInput-'));
                 if (input) {
                    const rect = input.getBoundingClientRect();
                    activeDropdown.style.top = `${rect.bottom + window.scrollY}px`;
                }
            }
        });

        // --- RECYCLE LOGIC (No changes needed, but included for completeness) ---

        function toggleRecycle(fieldName, event) {
            event.stopPropagation();
            recycleSettings[fieldName] = !recycleSettings[fieldName];
            updateAllRecycleButtons(fieldName);
        }

        function updateAllRecycleButtons(fieldName) {
            const isOn = recycleSettings[fieldName];
            const selector = `.recycle-${fieldName}`;
            
            document.querySelectorAll(selector).forEach(btn => {
                btn.classList.remove('btn-secondary', 'btn-warning');
                btn.classList.add(isOn ? 'btn-warning' : 'btn-secondary');
                btn.title = isOn 
                    ? `Recycling ON: Next rows will copy last value.` 
                    : `Recycling OFF: Click to copy last value to next rows.`;
            });
        }
        
        function initializeRecycleButtons() {
            updateAllRecycleButtons('expenseGroup');
            updateAllRecycleButtons('paymentAccount');
            updateAllRecycleButtons('pumpAttendant');
        }


        // --- NEW EXPENSE GROUP MODAL LOGIC (Modified to update all lists in body) ---

        function openNewGroupModal() {
            hideActiveDropdown(); // Ficha dropdown zote kabla ya kuonyesha modal
            const modalElement = document.getElementById('newExpenseGroupModal');
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }

        function saveNewExpenseGroup() {
            const newGroupName = document.getElementById('newGroupNameInput').value.trim();
            const newExpenseType = document.getElementById('newExpenseTypeSelect').value;

            if (!newGroupName) {
                toastr.error(lang('Tafadhali andika jina la Expense Group mpya','Please enter a name for the new Expense Group'), lang('Hitilafu','Error'), {timeOut: 2000});
                return;
            }

            const newId = 'NEW_' + (EXPENSE_GROUPS.length + 1);
            const newGroup = { 
                id: newId, 
                name: newGroupName, 
                type: newExpenseType 
            };
            EXPENSE_GROUPS.push(newGroup);

            // 1. Close Modal
            const modalElement = document.getElementById('newExpenseGroupModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();

            // 2. Update ALL existing options-list-dropdown elements attached to the body
            document.querySelectorAll('.options-list-dropdown').forEach(list => {
                // Hii ni simulation tu, hupaswi kufanya hivi katika production.
                // Inafanya kazi hapa kwa sababu orodha zote za expense group hutumia data sawa.
                if (list.id.includes('groupSelect')) { 
                    const newOptionHtml = `
                        <div class="searchable-option" 
                             data-value="${newGroup.id}" 
                             data-text="${newGroup.name}" 
                             data-type="${newGroup.type}">
                            ${newGroup.name}
                        </div>
                    `;
                    list.insertAdjacentHTML('beforeend', newOptionHtml);
                }
            });
            
            // 3. Clear modal inputs
            document.getElementById('newGroupNameInput').value = '';
            document.getElementById('newExpenseTypeSelect').value = 'CASH';
        }

        // --- CORE LOGIC ---

      const  readData = ()=>{ 
            // Populate Source Type dropdown
            const globalSourceSelect = document.getElementById('globalSourceType');
            SOURCE_TYPES.forEach(source => {
                const option = document.createElement('option');
                option.value = source.id;
                option.textContent = source.name;
                globalSourceSelect.appendChild(option);
            });
            calculateTotal();
            initializeRecycleButtons(); 
            // Check initial state of global select
            handleSelectColorChange(globalSourceSelect);
        };

        function initializeForm(sourceType) {
            currentSource = sourceType;
            rowCount = 0;
            
            const tableContainer = document.getElementById('expenseTableContainer');
            const tbody = document.getElementById('expenseRowsContainer');
            const thead = document.getElementById('expenseTable').querySelector('thead');
            const addRowBtn = document.getElementById('addRowBtn');
            const submitBtn = document.getElementById('submitBtn');
            const totalDisplay = document.getElementById('totalDisplay');
            const adjustPanel = document.getElementById('adjust_panel_forOptions');
            hideActiveDropdown(); // Ficha dropdown yoyote inayoonyeshwa

            // 1. Show controls and table
            tableContainer.classList.remove('hidden');
            addRowBtn.disabled = false;
            submitBtn.disabled = false;
            totalDisplay.classList.remove('hidden');
            adjustPanel.classList.remove('hidden');

            // 2. Clear existing rows
            tbody.innerHTML = '';
            
            // 3. Define the column headers based on source type
            let headers = ['#'];
            let widths = ['50px']; 

            if (sourceType === 'payment') {
                headers = [...headers, lang('Akaunti ya Malipo','Payment Account'), lang('Matumizi','Expense Group'), lang(`Kiasi (${fedha})`,`Amount (${fedha})`), lang('Mpokeaji','Receiver'), lang('Maelezo','Remarks'), lang('Hatua','Action')];
                widths = [...widths, '280px', '330px', '150px', '200px', 'auto', '80px'];
            } else if (sourceType === 'attendant') {
                headers = [...headers, lang('Mhusika wa Pampu','Pump Attendant'), lang('Matumizi','Expense Group'), lang(`Kiasi (${fedha})`,`Amount (${fedha})`), lang('Mpokeaji','Receiver'), lang('Maelezo','Remarks'), lang('Hatua','Action')];
                widths = [...widths, '280px', '330px', '150px', '200px', 'auto', '80px'];
            } else if (sourceType === 'fuel') {
                headers = [...headers, lang('Mhusika wa Pampu','Pump Attendant'), lang('Matumizi','Expense Group'),lang('Pampu','Pump'),lang('Mkono','Nozzle'),lang('kiasi(LTRS)','Quantity(LTRS)'), lang(`Kiasi (${fedha})`,`Amount (${fedha})`), lang('Mpokeaji','Receiver'), lang('Maelezo','Remarks'), lang('Hatua','Action')];
                widths = [...widths, '280px', '330px', '150px', '200px', 'auto', '80px'];
            }

            // 4. Build Table Header (<thead>)
            let headerHtml = '<tr>';
            headers.forEach((h, index) => {
                headerHtml += `<th scope="col" style="width:${widths[index]}">${h}</th>`;
            });
            headerHtml += '</tr>';
            thead.innerHTML = headerHtml;
            
            // 5. Add the first row automatically
            addRow();
            calculateTotal();
            initializeRecycleButtons(); 
        }


        function addRow() {
            if (!currentSource) return;

            const tbody = document.getElementById('expenseRowsContainer');
            const allRows = tbody.querySelectorAll('tr');
            const lastRowId = allRows.length > 0 ? parseInt(allRows[allRows.length - 1].id.split('-')[1]) : 0;
            
            const currentId = ++rowCount;
            let rowHtml = `<tr id="row-${currentId}">`;
            
            // --- Common Column: Row Number ---
            rowHtml += `<td>${currentId}</td>`;

            // --- Source-Specific Column 1 (Payment Account or Attendant) ---

            if (currentSource === 'payment') {
                // Payment Account (Searchable Select)
                rowHtml += `
                    <td class="source-cell">
                        ${createSearchableSelectHTML(
                            `paymentAccount-${currentId}`, 
                            `paymentAccount-${currentId}`, 
                            lang('Tafuta Akaunti...','Select Account'), 
                            PAYMENT_ACCOUNTS, 
                            'paymentAccount'
                        )}
                    </td>
                `;
            } else if (currentSource === 'attendant' || currentSource === 'fuel') {
                // Pump Attendant (Searchable Select)
                rowHtml += `
                    <td class="source-cell">
                        ${createSearchableSelectHTML(
                            `attendant-${currentId}`, 
                            `attendant-${currentId}`, 
                            lang('Tafuta Attendant...','Select Attendant'), 
                            ATTENDANTS, 
                            'pumpAttendant',
                            '',
                            'pumpAttendants'
                        )}
                    </td>
                `;
            } 
            
            // --- Common Column 2: Expense Group (Searchable Select with New Button) ---

            const newGroupButtonHtml = `
                <button type="button" class="btn btn-sm btn-info ms-2" onclick="openNewGroupModal()" title="Ongeza Group Jipya">New</button>
            `;

            EXPENSE_GROUPS = currentSource === 'fuel'
                ? EXPENSE_GROUPS.filter(g => g.mafuta)
                : EXPENSE_GROUPS;
            rowHtml += `
                <td class="expense-group-cell">
                    ${createSearchableSelectHTML(
                        `groupSelect-${currentId}`, 
                        `groupSelect-${currentId}`, 
                        lang('Tafuta Matumizi...','Search Expense'), 
                        EXPENSE_GROUPS, 
                        'expenseGroup', 
                        newGroupButtonHtml
                    )}
                </td>
            `;

            // --- Remaining Source-Specific Columns ---

            if (currentSource === 'payment' || currentSource === 'attendant') {
                // Amount (KES/TZS)
                rowHtml += `
                    <td>
                      <div class="wrapped">
                        <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                            <label class="mt-1 text-danger " for="amountInput-${currentId}"></label> 
                        <div class="box-pointer d-inline "></div>
                        </div>
                        <input id="amountInput-${currentId}" type="number" step="0.01" min="0" placeholder="0.00" class="form-control money-fomat form-control-sm" name="amount-${currentId}" required oninput="calculateTotal()">
                         </div>
                    </td>
                `;
            } 
            
            else if (currentSource === 'fuel') {
                
                // Fuel Pump (Select - Added onchange for color)
                rowHtml += `
                    <td>
                        <select id="pump-${currentId}" name="pump-${currentId}" 
                            onchange="populateNozzles(${currentId}, this.value); handleSelectColorChange(this)" 
                            class="form-select form-control smallerFont form-select-sm" required>
                            <option value="" disabled selected>${lang('Chagua Pump', 'Select Pump')}</option>
                            ${SELPUMPS.map(p => `<option value="${p.id}">${p.name}</option>`).join('')}
                        </select>
                    </td>
                `;

                // Pump Nozzle (Select, populated dynamically - Added onchange for color)
                rowHtml += `
                    <td>
                        <select id="nozzle-${currentId}" name="nozzle-${currentId}" 
                            onchange="handleFuelCalculation(${currentId}); handleSelectColorChange(this)" 
                            class="form-select form-select-sm form-control smallerFont" required>
                            <option value="" disabled selected>${lang('Chagua Nozzle','Select Nozzle')}</option>
                            
                        </select>
                    </td>
                `;
                
                // Qty (Litres) - Bidirectional
                rowHtml += `
                    <td>
                    <div class="wrapped">
                        <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                <label class="mt-1 text-danger " for="qtyInput-${currentId}"></label> 
                                <div class="box-pointer d-inline "></div>
                        </div>

                        <input id="qtyInput-${currentId}" type="number" step="0.0000001" min="0" placeholder="0.00" class="form-control money-fomat form-control-sm" name="quantity-${currentId}"  oninput="calculateAmount(${currentId})">
                     </div>
                  </td>
                `;
                
                // Amount (KES/TZS) - Bidirectional
                rowHtml += `
                    <td>
                    <div class="wrapped">
                            <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                <label class="mt-1 text-danger " for="price-${currentId}"></label> 
                                <div class="box-pointer d-inline "></div>
                            </div>

                        <input id="amountInput-${currentId}" type="number" step="0.01" min="0" placeholder="0.00" class="form-control money-fomat form-control-sm" name="amount-${currentId}" required oninput="calculateQty(${currentId})">
                        <input type="hidden" id="price-${currentId}" value="${PRICE_PER_LITRE_SIMULATED}">
                        </div>
                    </td>
                `;
            }

            // --- Common Columns (Receiver & Remarks) ---
            
            // Receiver
            rowHtml += `
                <td>
                    <input id="receiver-${currentId}" type="text" placeholder="${lang('Jina la mpokeaji','Receiver Name')}" class="form-control form-control-sm" name="receiver-${currentId}" required>
                </td>
            `;

            // Remarks
            rowHtml += `
                <td>
                    <textarea id="remarks-${currentId}" placeholder="${lang('Mfano: Matengenezo','Example: Repairs')}" class="form-control form-control-sm" name="remarks-${currentId}" ></textarea>
                </td>
            `;
            
            // Action Button
            rowHtml += `
                <td>
                    <button type="button" onclick="removeRow(${currentId})" class="btn btn-danger btn-sm" aria-label="Remove Expense">
                        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </td>
            `;

            rowHtml += `</tr>`;
            
            tbody.insertAdjacentHTML('beforeend', rowHtml);

            // --- ATTACH LISTENERS AND APPLY RECYCLE LOGIC ---
            
            // 1. Attach Search Listeners (Tukitumia data ya options inatakiwa kuwa parameter)
            attachSearchableSelectListeners(`groupSelect-${currentId}`, EXPENSE_GROUPS);
            if (currentSource === 'payment') {
                attachSearchableSelectListeners(`paymentAccount-${currentId}`, PAYMENT_ACCOUNTS);
            } else if (currentSource === 'attendant' || currentSource === 'fuel') {
                attachSearchableSelectListeners(`attendant-${currentId}`, ATTENDANTS);
            }

            // 2. Apply Recycle Values
            if (lastRowId > 0) { 
                const copyValue = (fieldIdBase, fieldName) => {
                    if (recycleSettings[fieldName]) {
                        const lastHiddenInput = document.getElementById(`hiddenValue-${fieldIdBase}-${lastRowId}`);
                        const currentHiddenInput = document.getElementById(`hiddenValue-${fieldIdBase}-${currentId}`);
                        const currentSearchInput = document.getElementById(`searchInput-${fieldIdBase}-${currentId}`);
                        
                        if (lastHiddenInput && currentHiddenInput && currentSearchInput) {
                            const lastValue = lastHiddenInput.value;
                            const lastText = lastHiddenInput.getAttribute('data-display-text');
                            
                            if (lastValue && lastText) {
                                currentHiddenInput.value = lastValue;
                                currentHiddenInput.setAttribute('data-display-text', lastText);
                                currentSearchInput.value = lastText;
                                currentSearchInput.classList.add('selected-text'); // Apply color
                            }
                        }
                    }
                };

                copyValue('groupSelect', 'expenseGroup');
                if (currentSource === 'payment') {
                    copyValue('paymentAccount', 'paymentAccount');
                }
                if (currentSource === 'attendant' || currentSource === 'fuel') {
                    copyValue('attendant', 'pumpAttendant');
                }
            }
            
            // 3. Set the correct colors for the recycle buttons in the new row
            initializeRecycleButtons();
        }
        
        // --- FUEL CALCULATION LOGIC (Source 3) ---

        /**
         * Populates the Nozzle dropdown based on the selected Pump.
         */
        function populateNozzles(rowId, pumpId) {
            const nozzleSelect = document.getElementById(`nozzle-${rowId}`);
            nozzleSelect.innerHTML = '<option value="" disabled selected>Chagua Nozzle</option>';
            nozzleSelect.classList.remove('selected-text'); // Clear color on new pump selection

            const selectedPump = SELPUMPS.find(p => Number(p.id) === Number(pumpId));
            if (selectedPump) {
                selectedPump.nozzles.forEach(n => {
                    const option = document.createElement('option');
                    option.value = n.id;
                    option.textContent = n.name;
                    option.setAttribute('data-price', n.price);
                    nozzleSelect.appendChild(option);
                });
            }
            
            document.getElementById(`qtyInput-${rowId}`).value = '';
            document.getElementById(`amountInput-${rowId}`).value = '';
            document.getElementById(`price-${rowId}`).value = PRICE_PER_LITRE_SIMULATED;
        }

        function setPumps(inputElement) {
            
            const rowId = inputElement.id.replace('searchInput-', '').replace('attendant-', '');
            const pumpSelect = document.getElementById(`pump-${rowId}`);
            
            pumpSelect.innerHTML = `<option value="" disabled selected>${lang('Chagua Pump','Select Pump')}</option>`;

            const shift = document.getElementById(inputElement.id.replace('searchInput-', 'hiddenValue-')).value;
            const availablePumps = PUMPS.filter(p => Number(p.shift) === Number(shift));
            

            // console.log({'Available Pumps': availablePumps,PUMPS,'Selected Shift/Attendant ID': shift});
           SELPUMPS = availablePumps;


            availablePumps.forEach(p => {
                const option = document.createElement('option');
                option.value = p.id;
                option.textContent = p.name;

                pumpSelect.appendChild(option);
            })
        }

        /**
         * Updates the hidden price field when a nozzle is selected.
         */
        function handleFuelCalculation(rowId) {
            const nozzleSelect = document.getElementById(`nozzle-${rowId}`);
            const selectedOption = nozzleSelect.options[nozzleSelect.selectedIndex];
            
            if (selectedOption && selectedOption.getAttribute('data-price')) {
                const price = parseFloat(selectedOption.getAttribute('data-price'));
                document.getElementById(`price-${rowId}`).value = price;
            }
            
            calculateAmount(rowId);
        }
        
        /**
         * Calculates Amount based on Qty input.
         */
        function calculateAmount(rowId) {
            const qtyInput = document.getElementById(`qtyInput-${rowId}`);
            const amountInput = document.getElementById(`amountInput-${rowId}`);
            const priceInput = document.getElementById(`price-${rowId}`);
            
            const qty = parseFloat(qtyInput.value);
            const price = parseFloat(priceInput.value);
            
            if (!isNaN(qty) && qty > 0 && !isNaN(price)) {
                const amount = qty * price;
                amountInput.value = amount.toFixed(2);
            } else {
                amountInput.value = '';
            }
            calculateTotal();
        }
        
        /**
         * Calculates Qty based on Amount input.
         */
        function calculateQty(rowId) {
            const qtyInput = document.getElementById(`qtyInput-${rowId}`);
            const amountInput = document.getElementById(`amountInput-${rowId}`);
            const priceInput = document.getElementById(`price-${rowId}`);
            
            const amount = parseFloat(amountInput.value);
            const price = parseFloat(priceInput.value);

            if (!isNaN(amount) && amount > 0 && !isNaN(price) && price > 0) {
                const qty = amount / price;
                qtyInput.value = qty.toFixed(2);
            } else {
                qtyInput.value = '';
            }
            calculateTotal();
        }

        // --- GENERAL FUNCTIONS ---

        function calculateTotal() {
            let total = 0;
            const rows = document.querySelectorAll('#expenseRowsContainer tr');

            // if (currentSource === 'payment' || currentSource === 'attendant') {
                rows.forEach(row => {
                    const rowId = row.id.split('-')[1];
                    const amountInput = document.getElementById(`amountInput-${rowId}`);
                    
                    if (amountInput) {
                        const amount = parseFloat(amountInput.value);
                        if (!isNaN(amount) && amount > 0) {
                            total += amount;
                        }
                    }
                });
            // }
        
         
            document.getElementById('totalAmount').textContent = Number(total.toFixed(2)).toLocaleString();
        }

        function removeRow(id) {
            if (document.getElementById(`row-${id}`)) {
                document.getElementById(`row-${id}`).remove();
                
                // Ondoa pia listi yake kutoka kwa body ili isibaki.
                const listId = `list-groupSelect-${id}`;
                const listElement = document.getElementById(listId);
                if(listElement) listElement.remove();
                
                // Fanya hivyo kwa kila listi
                ['paymentAccount', 'attendant'].forEach(base => {
                    const baseListId = `list-${base}-${id}`;
                    const baseListElement = document.getElementById(baseListId);
                    if(baseListElement) baseListElement.remove();
                });
            }
            calculateTotal();
        }
        
        document.getElementById('expenseForm').addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const data = {
                global_source_type: currentSource,
                total_monetary_expense: parseFloat(document.getElementById('totalAmount').textContent),
                expenses: []
            };
            
            const rows = document.querySelectorAll('#expenseRowsContainer tr');
            
            rows.forEach(row => {
                const rowId = row.id.split('-')[1];
                
                // Read values from hidden input for searchable fields
                const expenseGroupId = document.getElementById(`hiddenValue-groupSelect-${rowId}`)?.value || formData.get(`groupSelect-${rowId}`);
                const groupDetail = EXPENSE_GROUPS.find(g => g.id === expenseGroupId);

                const expense = {
                    expense_group_id: expenseGroupId,
                    expense_group_name: groupDetail ? groupDetail.name : 'Unknown Group',
                    expense_type: groupDetail ? groupDetail.type : 'N/A',
                    receiver_name: formData.get(`receiver-${rowId}`),
                    remarks: formData.get(`remarks-${rowId}`),
                    source_details: {}
                };

                if (currentSource === 'payment') {
                    expense.source_details.account_id = document.getElementById(`hiddenValue-paymentAccount-${rowId}`)?.value || formData.get(`paymentAccount-${rowId}`);
                    expense.amount_cash = parseFloat(formData.get(`amount-${rowId}`)) || 0;
                } else if (currentSource === 'attendant') {
                    expense.source_details.attendant_id = document.getElementById(`hiddenValue-attendant-${rowId}`)?.value || formData.get(`attendant-${rowId}`);
                    expense.amount_cash = parseFloat(formData.get(`amount-${rowId}`)) || 0;
                } else if (currentSource === 'fuel') {
                    expense.source_details.attendant_id = document.getElementById(`hiddenValue-attendant-${rowId}`)?.value || formData.get(`attendant-${rowId}`);
                    expense.source_details.pump_id = formData.get(`pump-${rowId}`);
                    expense.source_details.nozzle_id = formData.get(`nozzle-${rowId}`);
                    expense.quantity_litres = parseFloat(formData.get(`quantity-${rowId}`)) || 0;
                    expense.amount_total = parseFloat(formData.get(`amount-${rowId}`)) || 0;
                }
                
                data.expenses.push(expense);
            });

            // Display results in the output area
            const outputElement = document.getElementById('outputData');
            outputElement.textContent = JSON.stringify(data, null, 2);

            const toSend = {
                data: {
                     isFuel: Number(currentSource === 'fuel'),
                    isPumpAttendant: Number(currentSource === 'attendant'),
                    isPayment: Number(currentSource === 'payment'),
                    expDate: moment(moment(document.getElementById('expenseDate').value).format('YYYY-MM-DD 00:10:00')).format(),
                    expenses: JSON.stringify(data.expenses)
                },
                url:'/accounting/addExpense'
            }

           
            
            $('#loadMe').modal('show');
            const sendIt = POSTREQUEST(toSend);
            sendIt.then((res)=>{
                $('#loadMe').modal('hide');
                hideLoading();
                const msg = lang(res.message_swa, res.message_eng);
                if(res.success){
                    toastr.success(msg, lang('Imekamilika','Success'), {timeOut: 2000});
                    location.reload()
                }else{
                    toastr.error(msg, lang('Hitilafu','Error'), {timeOut: 3000});
                }
            });

            // Show the output section
            // document.getElementById('output').classList.remove('hidden');
            // document.getElementById('output').classList.add('d-block');

            // document.getElementById('output').scrollIntoView({ behavior: 'smooth' });
        });


// Handle New Expense Group Form Submission
document.getElementById('newExpenseGroupForm')?.addEventListener('submit', function(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const newGroupName = formData.get('expense_group_name')?.trim();
    const newExpenseType = Number($('#isFuelExp').prop('checked'));

    // console.log(newExpenseType);

    if (!newGroupName) {
        toastr.error(lang('Tafadhali andika jina la Expense Group mpya','Please enter a name for the new Expense Group'), lang('Hitilafu','Error'), {timeOut: 2000});
        return;
    }

    const toSend = {
        data: {
            groupName: newGroupName,
            isFuel: newExpenseType,
           
        },
        url: '/accounting/addExpenseGroup'
    };
    $('#newExpenseGroupModal').modal('hide');
    $('#loadMe').modal('show');

    const sendIt = POSTREQUEST(toSend);
    
    sendIt.then((res) => {
        $('#loadMe').modal('hide');
        hideLoading();
        
        const msg = lang(res.message_swa, res.message_eng);
        
        if(res.success){
            toastr.success(msg, lang('Imekamilika','Success'), {timeOut: 2000});
            
            // Add the new group to the local array
            const newGroup = {
                id: res.id ,
                name: newGroupName,
                type: newExpenseType,
                mafuta: newExpenseType
            };
            EXPENSE_GROUPS.push(newGroup);
            
            // Update all existing expense group dropdowns
            document.querySelectorAll('.options-list-dropdown').forEach(list => {
                if (list.id.includes('groupSelect')) {
                    const newOptionHtml = `
                        <div class="searchable-option" 
                             data-value="${newGroup.id}" 
                             data-text="${newGroup.name}" 
                             data-type="${newGroup.type}">
                            ${newGroup.name}
                        </div>
                    `;
                    list.insertAdjacentHTML('beforeend', newOptionHtml);
                }
            });
            
            // Close modal and reset form
            // const modalElement = document.getElementById('newExpenseGroupModal');
            // const modal = bootstrap.Modal.getInstance(modalElement);
            // modal.hide();
            event.target.reset();
            
        } else {
            toastr.error(msg, lang('Hitilafu','Error'), {timeOut: 3000});
        }
    }).catch((error) => {
        $('#loadMe').modal('hide');
        hideLoading();
        toastr.error(lang('Kuna hitilafu imetokea','An error occurred'), lang('Hitilafu','Error'), {timeOut: 3000});
        // console.error('Error:', error);
    });
});