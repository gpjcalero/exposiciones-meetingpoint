import os

filepath = r"c:\Users\ES00500148\Desktop\Antigravity\Exposiciones MeetingPoint\exposiciones-meetingpoint-main\index.html"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Replace importCSV selection logic
import_old = r"""onclick="document.querySelector('.overlay').remove();(${callback.toString()})('${s.id}')\""""
import_new = r"""onclick="window.__importCallback('${s.id}'); document.querySelector('.overlay').remove();\""""
text = text.replace(import_old, import_new)

import_fn_old = """function importCSV() {"""
import_fn_new = """function importCSV() {
  window.__importCallback = null;"""
if import_fn_old in text:
    text = text.replace(import_fn_old, import_fn_new, 1)

show_store_old = """showStoreSelector(storeId => {"""
show_store_new = """window.__importCallback = storeId => {"""
text = text.replace(show_store_old, show_store_new)

show_store_close_old = """        go('home');
      });
    };"""
show_store_close_new = """        go('home');
      };
      showStoreSelector();
    };"""
text = text.replace(show_store_close_old, show_store_close_new)


# Now REPLACE completely renderAudit and its associated functions
audit_start = "function renderAudit() {"
audit_end = "/* ── LOGS ──────────────────────────────────────────────────────── */"

def get_block(start_str, end_str, data):
    start_idx = data.find(start_str)
    if start_idx == -1: return ""
    end_idx = data.find(end_str, start_idx)
    return data[start_idx:end_idx]

old_audit_block = get_block(audit_start, audit_end, text)

new_audit_block = """function renderAudit() {
  const store = state.stores.find(s=>s.id===state.selStore);
  const box = (state.ambientes[store?.id]||[]).find(b=>b.id===state.selBox);
  if (!store||!box) { go('boxes'); return; }

  app().innerHTML = `<div class="anim-in">
    <div class="topbar">
      <button class="back-btn" onclick="go('materials')">${ICO.chevL}</button>
      <div style="flex:1;min-width:0"><h1>Escanear Etiquetas</h1><p class="sub">${box.name} · ${store.tienda}</p></div>
    </div>
    <div class="list">
      <div class="capture-zone" onclick="$('fileInput').click()" id="auditCaptureWrapper">
        <div style="width:64px;height:64px;border-radius:18px;background:var(--blue-bg);border:1px solid rgba(79,70,229,.2);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;color:var(--blue);box-shadow:0 4px 12px rgba(0,0,0,.04)">${ICO.camera}</div>
        <p style="font-size:15px;font-weight:700;color:var(--text)">Pulsa para escanear</p>
        <p style="font-size:12px;color:var(--text3);margin-top:6px">Detección de múltiples materiales</p>
      </div>
      <input type="file" id="fileInput" accept="image/*" capture="environment" style="display:none" onchange="handleCapture(this)">

      <div id="materialsList" style="display:flex;flex-direction:column;gap:16px;margin-top:12px;"></div>
      
      <div id="saveAllWrapper" class="hidden" style="margin-top:10px;">
        <button class="btn-primary" onclick="saveAllAudit()">${ICO.check} Guardar todos los materiales</button>
      </div>

      <p style="font-size:11px;color:var(--text4);font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin:24px 0 12px;text-align:center" id="manualText">O añadir manualmente</p>
      
      <button class="btn-secondary" id="btnManual" onclick="addManualItem()">+ Añadir material manual</button>
    </div>
  </div>`;
  
  state._auditItems = [];
}

const LOCS = ['MUR','SOL','ROBINETTERIE','CUISINE','MEUBLE','DOUCHE','WC','TERASSE','PRESENTOIR'];

function addManualItem(sap='', loc='', notes='', status='ACTIVO') {
  const id = Date.now() + Math.random();
  state._auditItems.push({ id, sap, loc, notes, status });
  renderAuditItems();
  $('auditCaptureWrapper').classList.add('hidden');
  $('manualText').classList.add('hidden');
  $('btnManual').classList.add('hidden');
}

function handleCapture(input) {
  const file = input.files?.[0];
  if (!file) return;
  toast('Analizando imagen...', 'info');
  
  // Simulate OCR finding 2-4 materials
  setTimeout(() => {
    $('auditCaptureWrapper').classList.add('hidden');
    $('manualText').classList.add('hidden');
    $('btnManual').classList.add('hidden');
    
    const count = Math.floor(Math.random() * 3) + 2; 
    for(let i=0; i<count; i++) {
       const fakeSap = '1003' + Math.floor(Math.random()*90000+10000);
       state._auditItems.push({ id: Date.now()+i, sap: fakeSap, loc: '', notes: '', status: 'ACTIVO' });
    }
    toast(`${count} materiales detectados`);
    renderAuditItems();
  }, 800);
}

function renderAuditItems() {
  const list = $('materialsList');
  if(!state._auditItems.length) return;
  
  list.innerHTML = state._auditItems.map((item, index) => `
    <div class="card" style="flex-direction:column;align-items:stretch;padding:16px;box-shadow:0 2px 10px rgba(0,0,0,.03);">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
         <h4 style="font-size:14px;color:var(--text);font-weight:800">Material #${index+1}</h4>
         <button class="trash-btn" style="padding:4px;" onclick="removeAuditItem(${item.id})">${ICO.trash}</button>
      </div>
      <div>
        <label class="label">Código SAP</label>
        <input class="input" value="${item.sap}" onchange="updateAuditItem(${item.id}, 'sap', this.value)" placeholder="Ej: 100336896">
      </div>
      <div style="margin-top:12px;">
        <label class="label">Colocación / Ubicación</label>
        <div class="chips" style="gap:6px;">
          ${LOCS.map(l => `<button class="chip ${item.loc===l?'active':''}" style="padding:6px 10px;font-size:11px;" onclick="updateAuditItem(${item.id}, 'loc', '${l}')">${l}</button>`).join('')}
        </div>
      </div>
    </div>
  `).join('');
  
  $('saveAllWrapper').classList.remove('hidden');
}

function updateAuditItem(id, field, value) {
  const item = state._auditItems.find(i => i.id === id);
  if(item) {
    item[field] = value;
    if(field === 'loc') renderAuditItems();
  }
}

function removeAuditItem(id) {
  state._auditItems = state._auditItems.filter(i => i.id !== id);
  renderAuditItems();
  if(!state._auditItems.length) {
    go('audit'); // Reset view
  }
}

function saveAllAudit() {
  const store = state.stores.find(s=>s.id===state.selStore);
  let saved = 0;
  for(const item of state._auditItems) {
     if(!item.sap.trim()) continue;
     addMaterial(store.id, state.selBox, item.sap.trim(), item.loc || 'SIN_UBICACION', item.notes, item.status);
     saved++;
  }
  if(saved > 0) {
    toast(`${saved} materiales guardados con éxito`);
    go('materials');
  } else {
    toast('No hay códigos SAP válidos para guardar', 'err');
  }
}

"""

if old_audit_block:
    text = text.replace(old_audit_block, new_audit_block)


with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)
