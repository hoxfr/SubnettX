import os

html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'index.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html_code = f.read()

original_leave_html = """<!-- Leave Application -->
                        <div class="card border border-slate-700 shadow-xl rounded-xl">
                            <h2 class="font-bold text-lg mb-2">Instant Leave Application Form</h2>
                            <p class="text-xs text-gray-500 mb-4">Submit official leave documents directly.</p>
                            <div class="space-y-4">
                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <label class="block text-[0.65rem] font-bold uppercase tracking-wider text-gray-500 mb-2">Roll Number</label>
                                        <input type="text" id="leave-roll" class="input-field text-xs" placeholder="e.g. 260307">
                                    </div>
                                    <div>
                                        <label class="block text-[0.65rem] font-bold uppercase tracking-wider text-gray-500 mb-2">Personal Email</label>
                                        <input type="email" id="leave-email" class="input-field text-xs" placeholder="anurag@gmail.com">
                                    </div>
                                </div>
                                <div>
                                    <label class="block text-[0.65rem] font-bold uppercase tracking-wider text-gray-500 mb-2">Target Professor</label>
                                    <select id="leave-target-prof" class="input-field text-xs">
                                        <option value="ski@6767">Prof. Skibidi Saxena (Faculty Chair - CSE)</option>
                                        <option value="riz@1234">Dr. Rizzler Rastogi (Faculty Co-Chair - MTH)</option>
                                        <option value="gya@9876">Prof. Kai Fanat (Humanities Head - COM)</option>
                                        <option value="sig@4567">Dr. Duke Jhatka (Mechanical Head - MEC)</option>
                                    </select>
                                </div>
                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <label class="block text-[0.65rem] font-bold uppercase tracking-wider text-gray-500 mb-2">Leave Start Date</label>
                                        <input type="date" id="leave-start-date" class="input-field text-xs">
                                    </div>
                                    <div>
                                        <label class="block text-[0.65rem] font-bold uppercase tracking-wider text-gray-500 mb-2">Leave End Date</label>
                                        <input type="date" id="leave-end-date" class="input-field text-xs">
                                    </div>
                                </div>
                                <div>
                                    <label class="block text-[0.65rem] font-bold uppercase tracking-wider text-gray-500 mb-2">Reason Description</label>
                                    <textarea id="leave-reason" class="input-field text-xs h-20 resize-none" placeholder="Reason for absence..."></textarea>
                                </div>
                                <div>
                                    <label class="block text-[0.65rem] font-bold uppercase tracking-wider text-gray-500 mb-2">Upload Verification Certificate</label>
                                    <input type="file" id="leave-file" class="input-field text-xs" accept=".png,.pdf">
                                </div>
                                <button onclick="submitLeave()" class="w-full btn-primary mt-2">Transmit Request</button>
                            </div>
                        </div>"""

leave_start = html_code.find("<!-- Leave Application -->")
if leave_start != -1:
    btn_idx = html_code.find("This module will be available in Phase 2.</p>", leave_start)
    if btn_idx != -1:
        end_div1 = html_code.find("</div>", btn_idx)
        end_div2 = html_code.find("</div>", end_div1 + 1) + 6 # Include the </div>
        orig_block = html_code[leave_start:end_div2]
        
        html_code = html_code.replace(orig_block, original_leave_html)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_code)
        print("Leave Application unlocked.")
    else:
        print("Could not find lock text.")
else:
    print("Could not find Leave Application block.")
