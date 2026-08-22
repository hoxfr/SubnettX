import os

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html_code = f.read()

maitri_html = """
                        <!-- Maitri Sync Engine -->
                        <div class="card border border-slate-700 shadow-xl rounded-xl mt-6">
                            <h2 class="font-bold text-lg mb-4 text-indigo-600">&#128452; Maitri ERP Sync Engine</h2>
                            
                            <!-- Step 1: Selection Form -->
                            <div id="maitri-step1" class="space-y-4">
                                <p class="text-[0.65rem] font-bold text-gray-500 uppercase tracking-wider mb-2">Automated ERP Attendance Propagation</p>
                                <div>
                                    <label class="block text-xs font-bold text-gray-700 mb-1">Select Academic Date</label>
                                    <input type="date" id="maitri-date" class="input-field text-xs">
                                </div>
                                <div>
                                    <label class="block text-xs font-bold text-gray-700 mb-1">Select Subject / Batch</label>
                                    <select id="maitri-subject" class="input-field text-xs">
                                        <option value="CSE1101">CSE1101 (CP IN C) - CSE II</option>
                                        <option value="MTH1801">MTH1801 (CALCULUS) - CSE II</option>
                                        <option value="COM1101">COM1101 (COMS) - CSE II</option>
                                        <option value="MEC1101">MEC1101 (EME) - CSE II</option>
                                        <option value="ENV1101">ENV1101 (EVS SUSTAIN) - CSE II</option>
                                        <option value="VAL1801">VAL1801 (ENG ETHICS) - CSE II</option>
                                        <option value="MAD1101">MAD1101 (DES.THINK) - CSE II</option>
                                    </select>
                                </div>
                                <button onclick="generateMaitriReport()" class="w-full btn-primary bg-indigo-600 hover:bg-indigo-700 border-none shadow-md transition-all">Check Attendance Report</button>
                            </div>

                            <!-- Step 2: Report & Sync -->
                            <div id="maitri-step2" class="hidden flex flex-col space-y-4">
                                <div class="bg-gray-50 p-4 rounded border border-gray-200">
                                    <h3 class="font-bold text-sm text-gray-800 mb-1" id="maitri-report-title">Report</h3>
                                    <p class="text-[0.65rem] text-gray-500 mb-3 border-b border-gray-200 pb-2 uppercase tracking-wider font-bold">Verifying local ledger against central DB...</p>
                                    <div class="grid grid-cols-2 gap-2 text-xs font-mono">
                                        <div class="text-gray-600">Total Enrollment:</div><div class="font-bold text-right">62</div>
                                        <div class="text-green-600">Verified Present:</div><div class="font-bold text-green-600 text-right" id="maitri-present">--</div>
                                        <div class="text-red-500">Marked Absent:</div><div class="font-bold text-red-500 text-right" id="maitri-absent">--</div>
                                        <div class="text-blue-500">On Leave (Med):</div><div class="font-bold text-blue-500 text-right">2</div>
                                    </div>
                                </div>
                                <div class="flex justify-end gap-2 mt-2">
                                    <button onclick="resetMaitriSync()" class="px-3 py-2 text-xs text-gray-500 hover:text-gray-800 font-bold uppercase">Cancel</button>
                                    <button id="btn-push-maitri" onclick="pushToMaitri()" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 text-xs font-bold uppercase rounded flex items-center gap-2 shadow-sm transition-all">
                                        <span>Add it on Maitri</span>
                                    </button>
                                </div>
                            </div>
                        </div>"""

maitri_js = """
        /* =========================================
           MAITRI SYNC ENGINE (DEMO)
           ========================================= */
        function generateMaitriReport() {
            const d = document.getElementById('maitri-date').value;
            const s = document.getElementById('maitri-subject').options[document.getElementById('maitri-subject').selectedIndex].text;
            if(!d || !s) return alert("Select Date and Subject first.");
            
            document.getElementById('maitri-step1').classList.add('hidden');
            document.getElementById('maitri-step2').classList.remove('hidden');
            
            document.getElementById('maitri-report-title').innerText = `${s} | ${d}`;
            
            const present = Math.floor(Math.random() * 8) + 48; 
            document.getElementById('maitri-present').innerText = present;
            document.getElementById('maitri-absent').innerText = 62 - present - 2;
        }

        function resetMaitriSync() {
            document.getElementById('maitri-step2').classList.add('hidden');
            document.getElementById('maitri-step1').classList.remove('hidden');
            document.getElementById('btn-push-maitri').innerHTML = `<span>Add it on Maitri</span>`;
            document.getElementById('btn-push-maitri').disabled = false;
        }

        function pushToMaitri() {
            const btn = document.getElementById('btn-push-maitri');
            btn.disabled = true;
            btn.innerHTML = `<svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> <span>Syncing...</span>`;
            
            setTimeout(() => {
                btn.innerHTML = `<span>&#10003; Synced</span>`;
                alert("Success: The attendance has been successfully added on the Maitri portal.");
                showToast("Maitri ERP sync complete.");
                setTimeout(() => resetMaitriSync(), 3000);
            }, 8000);
        }
"""

# Insert HTML before <!-- Right Column -->
insert_target = "<!-- Right Column -->"
if insert_target in html_code and "<!-- Maitri Sync Engine -->" not in html_code:
    html_code = html_code.replace(insert_target, maitri_html + "\n                    " + insert_target)

# Insert JS before closing script tag
script_target = "</script>\n</body>"
if script_target in html_code and "generateMaitriReport()" not in html_code:
    html_code = html_code.replace(script_target, maitri_js + "\n    " + script_target)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_code)
print("Maitri Sync Dashboard injected.")
