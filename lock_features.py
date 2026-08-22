import os

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html_code = f.read()

lock_html = """<div class="flex flex-col items-center justify-center py-8">
                                <svg class="w-10 h-10 text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8V7z"></path></svg>
                                <h3 class="text-md font-bold text-gray-400">Under Development</h3>
                                <p class="text-xs text-gray-400 text-center mt-1">This module will be available in Phase 2.</p>
                            </div>"""

# Classes Checkin
checkin_start = html_code.find("<!-- Classes Checkin -->")
checkin_end = html_code.find("<!-- Live Faculty Announcements Card -->")
if checkin_start != -1 and checkin_end != -1:
    orig_block = html_code[checkin_start:checkin_end]
    new_block = f"""<!-- Classes Checkin -->
                        <div class="card border border-slate-700 shadow-xl rounded-xl">
                            <h2 class="font-bold text-lg mb-4 text-gray-300">Classes Checkin</h2>
                            {lock_html}
                        </div>
                        """
    html_code = html_code.replace(orig_block, new_block)

# Crypto Ledger
ledger_start = html_code.find("<!-- Crypto Ledger -->")
ledger_end = html_code.find("<!-- Leave Application -->")
if ledger_start != -1 and ledger_end != -1:
    orig_block = html_code[ledger_start:ledger_end]
    new_block = f"""<!-- Crypto Ledger -->
                        <div class="card border border-slate-700 shadow-xl rounded-xl">
                            <h2 class="font-bold text-lg mb-2 text-gray-300">Cryptographic Digital Ledger</h2>
                            {lock_html}
                        </div>
                        """
    html_code = html_code.replace(orig_block, new_block)

# Leave Application
leave_start = html_code.find("<!-- Leave Application -->")
# Find the specific button to know the end of the block
btn_idx = html_code.find("Transmit Request</button>", leave_start)
if btn_idx != -1:
    end_div1 = html_code.find("</div>", btn_idx)
    end_div2 = html_code.find("</div>", end_div1 + 1) + 6 # Include the </div>
    orig_block = html_code[leave_start:end_div2]
    new_block = f"""<!-- Leave Application -->
                        <div class="card border border-slate-700 shadow-xl rounded-xl">
                            <h2 class="font-bold text-lg mb-2 text-gray-300">Leave Ticket Dashboard</h2>
                            {lock_html}
                        </div>"""
    html_code = html_code.replace(orig_block, new_block)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_code)
print("Locked features applied safely.")
