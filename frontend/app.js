const API_BASE = '' // mesmo host

function q(sel){return document.querySelector(sel)}

q('#nav-promocoes').addEventListener('click', ()=>show('promocoes'))
q('#nav-encartes').addEventListener('click', ()=>show('encartes'))
q('#nav-geocode').addEventListener('click', ()=>show('geocode'))

function show(id){document.querySelectorAll('.view').forEach(v=>v.classList.add('hidden')); q('#'+id).classList.remove('hidden')}

async function fetchPromocoes(){
  const res = await fetch(API_BASE + '/promocoes')
  const data = await res.json()
  const el = q('#lista-promocoes')
  el.innerHTML = ''
  data.forEach(p=>{
    const card = document.createElement('div'); card.className='card'
    card.innerHTML = `<h3>${p.produto}</h3><div class="muted">${p.loja} — ${p.cidade}</div><p>de ${p.preco_normal} por <strong>${p.preco_promo}</strong></p>`
    el.appendChild(card)
  })
}

async function fetchEncartes(){
  const res = await fetch(API_BASE + '/encartes')
  const data = await res.json()
  const el = q('#lista-encartes')
  el.innerHTML = ''
  data.forEach(e=>{
    const card = document.createElement('div'); card.className='card'
    card.innerHTML = `<h3>${e.loja}</h3><div class="muted">${e.cidade} — ${e.rede}</div><p><a href="${e.url_imagem}" target="_blank">Abrir encarte</a></p>`
    if(e.distancia_km) card.innerHTML += `<div class="muted">${e.distancia_km} km</div>`
    el.appendChild(card)
  })
}

q('#form-cep').addEventListener('submit', async (ev)=>{
  ev.preventDefault()
  const cep = q('#cep').value.trim()
  if(!cep) return
  const res = await fetch(API_BASE + '/geocodificar?cep=' + encodeURIComponent(cep))
  const data = await res.json()
  q('#resultado-cep').textContent = JSON.stringify(data, null, 2)
})

// inicial
show('promocoes')
fetchPromocoes()
fetchEncartes()
