import os

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html_code = f.read()

orig_classes = """<!-- Classes Checkin -->
                        <div class="card border border-slate-700 shadow-xl rounded-xl">
                            <h2 class="font-bold text-lg mb-4">Classes Checkin</h2>
                            <select id="subject-selector" class="input-field text-xs mb-4" onchange="runCheckin()">
                                <option value="CSE1101">CSE1101: Computer Programming using C</option>
                                <option value="MTH1801">MTH1801: Calculus for Engineers</option>
                                <option value="COM1101">COM1101: Communication and Writing Skills</option>
                                <option value="MEC1101">MEC1101: Elements of Mechanical Engineering</option>
                                <option value="VAL1801">VAL1801: Engineering Ethics</option>
                                <option value="ENV1101">ENV1101: Environmental Science</option>
                                <option value="MAD1101">MAD1101: Design Thinking</option>
                            </select>
                            <div class="flex justify-between items-center border-b border-gray-100 pb-2 mb-2">
                                <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Total Semester Classes</span>
                                <span id="disp-sem" class="font-mono font-bold text-sm">--</span>
                            </div>
                            <div class="flex justify-between items-center border-b border-gray-100 pb-2 mb-2">
                                <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Classes Conducted</span>
                                <span id="disp-cond" class="font-mono font-bold text-sm">--</span>
                            </div>
                            <div class="flex justify-between items-center border-b border-gray-100 pb-2 mb-4">
                                <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Classes Attended</span>
                                <input type="number" id="manual-attended-input" min="0" value="11" onchange="updateAttendedValueLive(this.value)" class="w-16 text-right font-bold border border-slate-300 rounded px-1 text-sm bg-white focus:outline-none">
                            </div>
                            <div class="grid grid-cols-2 gap-4">
                                <div class="bg-gray-50 border border-gray-200 p-4 rounded text-center flex flex-col justify-center">
                                    <div class="text-[0.65rem] font-bold text-gray-500 uppercase tracking-wider mb-1">Current %</div>
                                    <div id="disp-perc" class="text-3xl font-black text-[#0f172a]">--%</div>
                                </div>
                                <div class="bg-gray-50 border border-gray-200 p-4 rounded text-center flex flex-col justify-center">
                                    <div class="text-[0.65rem] font-bold text-gray-500 uppercase tracking-wider mb-1">Target: 80%</div>
                                    <div id="disp-meter" class="text-xs font-bold mt-1">--</div>
                                </div>
                            </div>
                            <div id="bunks-capacitator-container"></div>
                        </div>"""

orig_crypto = """<!-- Crypto Ledger -->
                        <div class="card border border-slate-700 shadow-xl rounded-xl">
                            <h2 class="font-bold text-lg mb-2">Cryptographic Digital Ledger</h2>
                            <p class="text-xs text-gray-500 mb-4">Tamper-proof verifiable attendance receipts.</p>
                            <table class="w-full text-left text-xs">
                                <thead class="uppercase text-gray-500 border-b border-gray-200">
                                    <tr><th class="pb-2">Date</th><th class="pb-2">Course</th><th class="pb-2">Action</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td class="py-3 font-mono">2026-08-18</td><td class="py-3 font-mono">CS301</td><td><button class="text-xs font-bold text-blue-600 uppercase border border-blue-600 px-2 py-1 rounded hover:bg-blue-600 hover:text-white transition">Download</button></td></tr>
                                </tbody>
                            </table>
                        </div>"""

# Replace Classes Checkin
start = html_code.find("<!-- Classes Checkin -->")
end = html_code.find("<!-- Live Faculty Announcements Card -->")
if start != -1 and end != -1:
    orig_block = html_code[start:end]
    html_code = html_code.replace(orig_block, orig_classes + "\n                        \n                        ")
    print("Classes Checkin unlocked")

# Replace Crypto Ledger
start = html_code.find("<!-- Crypto Ledger -->")
end = html_code.find("<!-- Leave Application -->")
if start != -1 and end != -1:
    orig_block = html_code[start:end]
    html_code = html_code.replace(orig_block, orig_crypto + "\n                        ")
    print("Crypto Ledger unlocked")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_code)
