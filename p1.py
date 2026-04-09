import os

filepath = r"c:\Users\ES00500148\Desktop\Antigravity\Exposiciones MeetingPoint\exposiciones-meetingpoint-main\index.html"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Replace delStore
t_delStore_old = """function delStore(id) {
  showConfirm('Eliminar tienda', state.stores.find(s=>s.id===id)?.tienda||'', ()=>{
    state.stores = state.stores.filter(s=>s.id!==id);
    delete state.ambientes[id]; delete state.materials[id];
    saveState(); renderStores(); toast('Tienda eliminada','info');
  });
}"""
t_delStore_new = """function delStore(id) {
  showConfirm('Eliminar tienda', state.stores.find(s=>s.id===id)?.tienda||'', ()=>{
    state.stores = state.stores.filter(s=>s.id!==id);
    delete state.ambientes[id]; delete state.materials[id]; delete state.photos[id];
    saveState(); renderStores(); toast('Tienda eliminada','info');
    fetch('/api/stores?id='+id, {method:'DELETE'}).catch(console.error);
  });
}"""
if t_delStore_old in text:
    text = text.replace(t_delStore_old, t_delStore_new)

# Replace delBox
t_delBox_old = """function delBox(id) {
  const store = state.stores.find(s=>s.id===state.selStore);
  const boxes = state.ambientes[store.id]||[];
  const box = boxes.find(b=>b.id===id);
  showConfirm('Eliminar ambiente', box?.name||'', ()=>{
    state.ambientes[store.id] = boxes.filter(b=>b.id!==id);
    if (state.materials[store.id]) delete state.materials[store.id][id];
    saveState(); renderBoxes(); toast('Ambiente eliminado','info');
  });
}"""
t_delBox_new = """function delBox(id) {
  const store = state.stores.find(s=>s.id===state.selStore);
  const boxes = state.ambientes[store.id]||[];
  const box = boxes.find(b=>b.id===id);
  showConfirm('Eliminar ambiente', box?.name||'', ()=>{
    state.ambientes[store.id] = boxes.filter(b=>b.id!==id);
    if (state.materials[store.id]) delete state.materials[store.id][id];
    if (state.photos[store.id]) delete state.photos[store.id][id];
    saveState(); renderBoxes(); toast('Ambiente eliminado','info');
    fetch('/api/boxes?id='+id, {method:'DELETE'}).catch(console.error);
  });
}"""
if t_delBox_old in text:
    text = text.replace(t_delBox_old, t_delBox_new)

# Replace delMat
t_delMat_old = """function delMat(boxId, idx) {
  const store = state.stores.find(s=>s.id===state.selStore);
  const mats = (state.materials[store.id]||{})[boxId]||[];
  if (mats[idx]) {
    mats.splice(idx, 1);
    saveState(); renderMaterials(); toast('Material eliminado','info');
  }
}"""
t_delMat_new = """function delMat(boxId, idx) {
  const store = state.stores.find(s=>s.id===state.selStore);
  const mats = (state.materials[store.id]||{})[boxId]||[];
  if (mats[idx]) {
    const sap = mats[idx].sapCode;
    mats.splice(idx, 1);
    saveState(); renderMaterials(); toast('Material eliminado','info');
    fetch('/api/materials?sap='+sap+'&box_id='+boxId, {method:'DELETE'}).catch(console.error);
  }
}"""
if t_delMat_old in text:
    text = text.replace(t_delMat_old, t_delMat_new)


# Replace renderHome
t_renderHome_start = "function renderHome() {"
t_renderHome_end = "    </div>`;\n}"
t_renderHome_old = text[text.find(t_renderHome_start):text.find(t_renderHome_end, text.find(t_renderHome_start)) + len(t_renderHome_end)]
t_renderHome_new = """function renderHome() {
  const active = state.stores.filter(s=>s.actividad==='Activo').length;
  const totalBoxes = Object.keys(state.ambientes).reduce((n,k)=>(state.ambientes[k]||[]).length+n,0);
  const totalMats = Object.keys(state.materials).reduce((n,k)=>{
    const mats = state.materials[k]||{};
    return n + Object.values(mats).reduce((m,arr)=>m+arr.length,0);
  },0);

  app().innerHTML = `
    <div class="anim-in">
      <div style="padding:48px 24px 24px">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
          <div class="avatar" style="border-radius:24px"><img src="https://ui-avatars.com/api/?name=Porcelanosa&background=EEF2FF&color=4F46E5&font-size=0.5" alt="Avatar"></div>
          <div>
            <span style="font-size:12px;font-weight:600;color:var(--text3)">Bienvenido</span>
            <h1 style="font-size:22px;font-weight:800;color:var(--text);line-height:1.2">Porcelanosa</h1>
          </div>
        </div>
        <p style="font-size:13px;color:var(--text3);letter-spacing:.05em;font-weight:600">AUDITORÍA DE SHOWROOMS</p>
      </div>
      <div style="padding:0 20px 80px;display:flex;flex-direction:column;gap:12px">
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:12px">
          <div class="card" style="flex-direction:column;cursor:default;text-align:center;padding:18px 8px">
            <span style="font-size:26px;font-weight:800;color:var(--text)">${state.stores.length}</span>
            <span style="font-size:10px;font-weight:700;color:var(--text3);text-transform:uppercase;margin-top:4px">Tiendas</span>
          </div>
          <div class="card" style="flex-direction:column;cursor:default;text-align:center;padding:18px 8px">
            <span style="font-size:26px;font-weight:800;color:var(--green)">${active}</span>
            <span style="font-size:10px;font-weight:700;color:var(--text3);text-transform:uppercase;margin-top:4px">Activas</span>
          </div>
          <div class="card" style="flex-direction:column;cursor:default;text-align:center;padding:18px 8px">
            <span style="font-size:26px;font-weight:800;color:var(--blue)">${totalMats}</span>
            <span style="font-size:10px;font-weight:700;color:var(--text3);text-transform:uppercase;margin-top:4px">Materiales</span>
          </div>
        </div>

        <div class="card" onclick="go('stores')">
          <div class="ico-box blue">${ICO.store}</div>
          <div style="flex:1"><div class="card-title">Gestión de Tiendas</div><div class="card-sub">${state.stores.length} en el maestro</div></div>
          <span class="chevron">${ICO.chevR}</span>
        </div>
        <div class="card" onclick="go('logs')">
          <div class="ico-box yellow">${ICO.history}</div>
          <div style="flex:1"><div class="card-title">Historial de Auditorías</div><div class="card-sub">${state.logs.length} registros recientes</div></div>
          <span class="chevron">${ICO.chevR}</span>
        </div>

        <button onclick="doExport()" class="btn-primary" style="margin-top:14px;background:var(--white);color:var(--text);border:1px solid var(--border);box-shadow:0 2px 8px rgba(0,0,0,.02)">
          <span style="display:flex;align-items:center;justify-content:center;gap:8px">${ICO.export} Exportar Auditoría (.csv)</span>
        </button>

        <button onclick="importCSV()" class="btn-primary" style="background:var(--white);color:var(--text);border:1px solid var(--border);box-shadow:0 2px 8px rgba(0,0,0,.02)">
          <span style="display:flex;align-items:center;justify-content:center;gap:8px">${ICO.upload} Importar materiales (.csv)</span>
        </button>

        <button onclick="resetAll()" style="width:100%;padding:10px;border-radius:10px;background:transparent;border:none;color:var(--text3);font-size:12px;font-weight:600;font-family:inherit;cursor:pointer;margin-top:8px">
          Restaurar datos maestro
        </button>
      </div>
    </div>`;
}"""
if t_renderHome_old in text:
    text = text.replace(t_renderHome_old, t_renderHome_new)

# Replace renderBoxes
t_renderBoxes_start = "function renderBoxes() {"
t_renderBoxes_end = "    </div>`;\n  });\n}" # Actually it ends with } from showAddBox too... let's just do it string literal.
# wait, better to replace just the html var logic and handleAmbientPhoto
renderBoxes_old = """const html = boxes.length === 0
    ? `<div class="empty"><div class="empty-ico">${ICO.box}</div><p class="empty-text">Sin ambientes</p><p style="font-size:11px;color:var(--text4);margin-top:4px">Pulsa + para añadir BOX</p></div>`
    : boxes.map((b,i) => {
        const mats = (state.materials[store.id]||{})[b.id] || [];
        const hasMats = mats.length > 0;
        return `<div class="card anim-up" style="animation-delay:${i*30}ms" onclick="go('materials',{selBox:'${b.id}'})">
          <div class="ico-box ${hasMats?'green':'yellow'}">${hasMats?ICO.check:ICO.box}</div>
          <div style="flex:1;min-width:0">
            <div class="card-title">${b.name}</div>
            <div class="card-sub">${hasMats?`<span style="color:var(--green);font-weight:600">${mats.length} materiales</span>`:`<span style="color:var(--yellow)">Sin materiales</span>`}</div>
          </div>
          <button class="scan-btn" onclick="event.stopPropagation();go('audit',{selBox:'${b.id}'})">${ICO.scan} Escanear</button>
          <button class="trash-btn" onclick="event.stopPropagation();delBox('${b.id}')">${ICO.trash}</button>
          <span class="chevron">${ICO.chevR}</span>
        </div>`;
      }).join('');"""
renderBoxes_new = """const html = boxes.length === 0
    ? `<div class="empty"><div class="empty-ico">${ICO.box}</div><p class="empty-text">Sin ambientes</p><p style="font-size:12px;color:var(--text3);margin-top:4px">Pulsa + para añadir BOX</p></div>`
    : boxes.map((b,i) => {
        const mats = (state.materials[store.id]||{})[b.id] || [];
        const hasMats = mats.length > 0;
        const photo = (state.photos && state.photos[store.id] && state.photos[store.id][b.id]) ? state.photos[store.id][b.id] : null;
        return `<div class="card anim-up" style="animation-delay:${i*30}ms;flex-direction:column;align-items:stretch" onclick="go('materials',{selBox:'${b.id}'})">
          ${photo ? `<img src="${photo}" class="ambient-photo">` : ''}
          <div style="display:flex;align-items:center;gap:12px;width:100%">
            <div class="ico-box ${hasMats?'green':'yellow'}">${hasMats?ICO.check:ICO.box}</div>
            <div style="flex:1;min-width:0">
              <div class="card-title">${b.name}</div>
              <div class="card-sub">${hasMats?`<span style="color:var(--green);font-weight:700">${mats.length} materiales</span>`:`<span style="color:var(--yellow);font-weight:600">Sin materiales</span>`}</div>
            </div>
            <span class="chevron">${ICO.chevR}</span>
          </div>
          <div style="display:flex;gap:8px;margin-top:6px">
            <button class="scan-btn" style="flex:1;justify-content:center" onclick="event.stopPropagation();go('audit',{selBox:'${b.id}'})">${ICO.scan} Escanear</button>
            <button class="photo-btn" style="flex:1;justify-content:center" onclick="event.stopPropagation();$('photoInput_'+'${b.id}').click()">${ICO.camera} Foto</button>
            <button class="trash-btn" onclick="event.stopPropagation();delBox('${b.id}')">${ICO.trash}</button>
          </div>
          <input type="file" id="photoInput_${b.id}" accept="image/*" capture="environment" style="display:none" onchange="handleAmbientPhoto(this, '${store.id}', '${b.id}')">
        </div>`;
      }).join('');"""
text = text.replace(renderBoxes_old, renderBoxes_new)

photo_handler = """function handleAmbientPhoto(input, storeId, boxId) {
  const file = input.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    if (!state.photos) state.photos = {};
    if (!state.photos[storeId]) state.photos[storeId] = {};
    state.photos[storeId][boxId] = ev.target.result;
    saveState();
    renderBoxes();
    toast('Foto de ambiente guardada');
    fetch('/api/photos', {method:'POST', body:JSON.stringify({id:Date.now()+'',store_id:storeId,box_id:boxId,photo_data:ev.target.result})}).catch(console.error);
  };
  reader.readAsDataURL(file);
}

function delBox"""
text = text.replace("function delBox", photo_handler)


with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)
