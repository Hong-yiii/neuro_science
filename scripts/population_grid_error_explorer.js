/* Offline explorer of authenticated, saved aggregate predictions. No network. */
(() => {
  'use strict';
  const D = JSON.parse(document.getElementById('error-analysis-data').textContent);
  const $ = id => document.getElementById('ea-' + id);
  const esc = x => String(x).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const names = {raw:'Raw',pca:'PCA7',cebra:'CEBRA-Time7',native:'Native multisession7',logistic:'Logistic',svm:'RBF-SVM',knn:'kNN5',lda:'SVD-LDA'};
  const pct = x => x === null || x === undefined ? 'Not evaluated' : (100 * x).toFixed(1) + '%';
  const num = (x,n=3) => x === null || x === undefined ? 'Undefined' : Number(x).toFixed(n);
  const mean = a => a.reduce((s,x)=>s+x,0)/a.length;
  const rep = s => s.decoder === 'logistic' ? s.encoder : s.encoder + '_' + s.decoder;
  const cid = (s,k=s.k,roster=s.roster,policy=s.policy) => s.world === 'observed' ? `observed_seed${s.seed}_K${k}_${roster}_${policy}` : `permuted${s.world}_seed0_K${k}_${roster}_${policy}`;
  const state = () => ({k:+$('k').value,roster:$('roster').value,policy:$('policy').value,encoder:$('encoder').value,decoder:$('decoder').value,head:$('head').value,seed:+$('seed').value,world:$('world').value,split:$('split').value,mode:$('mode').value,transition:$('transition').value,cut:$('cut').value});
  const matrix = (s,k=s.k,roster=s.roster,policy=s.policy) => D.matrices[cid(s,k,roster,policy)]?.[rep(s)]?.[s.head];
  const counts = (s,k=s.k,roster=s.roster,policy=s.policy) => matrix(s,k,roster,policy)?.[s.split];
  const labelsFor = k => D.panels.find(p=>p.class_count===k).conditions;
  const txt = (x,y,label,extra='') => `<text x="${x}" y="${y}" ${extra}>${esc(label)}</text>`;
  const cellColor = p => `rgb(${Math.round(248-220*p)},${Math.round(250-146*p)},${Math.round(251-113*p)})`;
  function table(headers,rows) {
    return '<div class="ea-scroll"><table><thead><tr>'+headers.map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+r.map(x=>'<td>'+esc(x)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>';
  }
  function matrixSVG(s,k=s.k,roster=s.roster,small=false) {
    const m=matrix(s,k,roster),a=counts(s,k,roster);
    if(!a) return '<p class="ea-missing">'+(m?'This control was fitted; its training matrix is not included in this view.':'This configuration was not fitted in the original grid.')+' No matrix is imputed.</p>';
    const n=m.labels.length,cell=540/n,left=95,top=90;
    const [from,to]=s.transition.split('-').map(Number);
    const removed=new Set(s.head==='pair'&&k===from?labelsFor(from).filter(x=>!labelsFor(to).includes(x)):[]);
    let out='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 725" role="img" aria-label="True classes by predicted classes confusion matrix" class="ea-matrix">';
    out+=txt(365,24,`K${k} · ${roster} · ${s.policy} · ${names[s.encoder]} / ${names[s.decoder]}`,'text-anchor="middle" font-size="16"');
    out+=txt(365,45,`${s.split} · ${s.head} · ${s.world==='observed'?'seed '+s.seed:'null '+s.world}`,'text-anchor="middle" font-size="13"');
    out+=txt(365,707,'Predicted class','text-anchor="middle" font-size="15"');
    out+=txt(20,360,'True class','text-anchor="middle" font-size="15" transform="rotate(-90 20 360)"');
    a.forEach((row,i)=>{
      const total=row.reduce((x,y)=>x+y,0),color=removed.has(m.labels[i])?'#a14017':'#243d46';
      out+=txt(left-8,top+(i+.65)*cell,m.labels[i].replace('->','→')+(removed.has(m.labels[i])?'*':''),`text-anchor="end" font-size="${Math.min(13,cell*.63)}" fill="${color}"`);
      out+=txt(left+(i+.6)*cell,top+540+12,m.labels[i].replace('->','→')+(removed.has(m.labels[i])?'*':''),`text-anchor="end" font-size="${Math.min(13,cell*.63)}" fill="${color}" transform="rotate(-60 ${left+(i+.6)*cell} ${top+552})"`);
      row.forEach((value,j)=>{
        const p=value/total,x=left+j*cell,y=top+i*cell;
        const title=`True ${m.labels[i]}, predicted ${m.labels[j]}: ${value}/${total} rows (${(100*p).toFixed(1)}%)`;
        out+=`<rect x="${x}" y="${y}" width="${cell}" height="${cell}" fill="${cellColor(p)}" stroke="${i===j?'#779d89':'#e5ecec'}" stroke-width="${i===j?1:.35}"><title>${esc(title)}</title></rect>`;
        if(!small&&value)out+=txt(x+cell/2,y+cell*.65,s.mode==='counts'?value:(100*p).toFixed(1),`text-anchor="middle" font-size="${Math.min(16,cell*.46)}" fill="${p>.55?'white':'#173541'}"`);
      });
    });
    return out+'</svg>';
  }
  function recallInfo(s,caseId=cid(s)) {
    const m=D.matrices[caseId]?.[rep(s)]?.pair;
    if(!m?.development||!m?.train)return [];
    return m.labels.map((label,i)=>{
      const u=D.usage[caseId][label],dv=m.development[i],tr=m.train[i],wrong=dv.map((v,j)=>i===j?0:v),max=Math.max(...wrong);
      return {label,train:tr[i]/tr.reduce((a,b)=>a+b,0),dev:dv[i]/dv.reduce((a,b)=>a+b,0),usage:u,
        mistake:max?m.labels[wrong.indexOf(max)]:'None',mistakeN:max};
    });
  }
  function main(s) {
    $('matrix').innerHTML=matrixSVG(s);
    const m=matrix(s),a=counts(s);
    if(a){
      const total=a.flat().reduce((x,y)=>x+y,0),correct=a.reduce((v,row,i)=>v+row[i],0),ba=mean(a.map((row,i)=>row[i]/row.reduce((x,y)=>x+y,0)));
      const g=D.grid.find(g=>g.class_count===s.k&&g.roster===s.roster),u=D.usage[cid(s)];
      const sourceText=u?' Training sources '+Object.values(u).reduce((v,r)=>v+r.train_used_sources,0)+'/'+Object.values(u).reduce((v,r)=>v+r.available_train_sources,0)+' used/available; development sources '+Object.values(u).reduce((v,r)=>v+r.development_used_sources,0)+'/'+Object.values(u).reduce((v,r)=>v+r.available_development_sources,0)+' used/available.':'';
      $('matrix-note').textContent=`${correct}/${total} constructed rows correct; balanced accuracy ${pct(ba)}. Rows=true, columns=predicted. Numbers show ${s.mode==='counts'?'row counts':'row-normalized percentages'}; color always shows row fraction on the same0–100% scale. * marks source-task pair labels removed in the selected class transition. Hover a cell for exact counts. No rows or labels are dropped from a displayed matrix. ${g.units} recorded columns/${g.sessions} sessions.${sourceText}`;
      $('matrix-table').innerHTML=table(['True class','Correct / total','Recall','Most frequent wrong prediction'],m.labels.map((label,i)=>{
        const row=a[i],wrong=row.map((v,j)=>i===j?0:v),max=Math.max(...wrong);
        return [label,row[i]+' / '+row.reduce((x,y)=>x+y,0),pct(row[i]/row.reduce((x,y)=>x+y,0)),max?m.labels[wrong.indexOf(max)]+' ('+max+')':'None'];
      }));
    }else{$('matrix-note').textContent=m?'Training predictions exist for this fitted control, but its training matrix is not included in this observed-training audit.':'This configuration was not fitted. Diagnostic control cases exist for full-roster U2/F16 only.';$('matrix-table').innerHTML='';}
    $('grid').innerHTML=[30,20,15].map(k=>['S33','S67','S100'].map(roster=>{
      const g=D.grid.find(g=>g.class_count===k&&g.roster===roster);
      return `<div class="ea-grid-card"><button type="button" data-k="${k}" data-roster="${roster}">Inspect K${k} ${roster} · ${g.units} columns / ${g.sessions} sessions</button>${matrixSVG(s,k,roster,true)}</div>`;
    }).join('')).join('');
  }
  function deletions(s) {
    if(s.world!=='observed'){$('deletion-summary').textContent='Class-deletion comparisons are descriptive observed-data comparisons only.';$('deletion-table').innerHTML='';return;}
    const [from,to]=s.transition.split('-').map(Number),a=recallInfo(s,cid(s,from)),b=recallInfo(s,cid(s,to));
    const destinations=new Map(b.map(r=>[r.label,r])),kept=a.filter(r=>destinations.has(r.label)),dropped=a.filter(r=>!destinations.has(r.label));
    const m=D.matrices[cid(s,from)][rep(s)].pair,deletedIndices=m.labels.map((label,i)=>!destinations.has(label)?i:-1).filter(i=>i>=0);
    let mistaken=0,allErrors=0,allRows=0;
    kept.forEach(r=>{const i=m.labels.indexOf(r.label),row=m.development[i];mistaken+=deletedIndices.reduce((x,j)=>x+row[j],0);allRows+=row.reduce((x,y)=>x+y,0);allErrors+=row.reduce((x,y)=>x+y,0)-row[i];});
    $('deletion-summary').textContent=`${from}→${to}, ${s.roster}/${s.policy}, seed${s.seed}, ${names[s.encoder]}/${names[s.decoder]}. In the source task: retained${kept.length} classes averaged${pct(mean(kept.map(r=>r.dev)))} recall; deleted${dropped.length} averaged${pct(mean(dropped.map(r=>r.dev)))}. Destination retained-class recall: ${pct(mean(b.map(r=>r.dev)))}. On retained source-task classes, ${mistaken}/${allErrors} errors pointed to a subsequently deleted label (${mistaken}/${allRows} evaluated rows). These are different tasks/cohorts, not paired examples or a causal deletion effect. Deleted classes have no destination prediction.`;
    $('deletion-table').innerHTML=table(['Pair class','Selection','Before recall','After recall','Available train sources before / after','Training reuse before / after','Before: common mistake'],a.map(r=>{
      const after=destinations.get(r.label);return [r.label,after?'Retained':'Deleted',pct(r.dev),after?pct(after.dev):'Not evaluated',r.usage.available_train_sources+' / '+(after?after.usage.available_train_sources:'Not evaluated'),pct(r.usage.train_reuse_fraction)+' / '+(after?pct(after.usage.train_reuse_fraction):'Not evaluated'),r.mistake+' ('+r.mistakeN+')'];
    }));
  }
  function reuse(s) {
    if(s.world!=='observed'){$('reuse-note').textContent='Support/error associations are defined here only for observed pair-head results.';$('reuse-plot').innerHTML='';$('reuse-table').innerHTML='';$('rho-table').innerHTML='';$('policy-flips').innerHTML='<p>Paired policy switches are shown for observed cases only.</p>';return;}
    const rs=recallInfo(s),variable=$('xaxis').value,values=rs.map(r=>r.usage[variable]),lo=Math.min(...values),hi=Math.max(...values),span=hi-lo||1;
    const X=x=>80+(hi===lo?.5:(x-lo)/span)*740,Y=y=>300-240*y;
    let svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 370" role="img" aria-label="Source reuse or support versus class development error">';
    [0,.25,.5,.75,1].forEach(v=>{svg+=`<line x1="80" x2="820" y1="${Y(v)}" y2="${Y(v)}" stroke="#dce6e3"/>`+txt(65,Y(v)+5,pct(v),'text-anchor="end"');});
    const tick=variable.includes('fraction')?pct:x=>num(x,1);
    [...new Set([lo,(lo+hi)/2,hi])].forEach(v=>{svg+=txt(X(v),327,tick(v),'text-anchor="middle"');});
    rs.forEach(r=>{svg+=`<circle cx="${X(r.usage[variable])}" cy="${Y(1-r.dev)}" r="5" fill="#256981" fill-opacity=".75"><title>${esc(r.label)}: ${esc(tick(r.usage[variable]))}; error ${pct(1-r.dev)}</title></circle>`;svg+=txt(X(r.usage[variable])+7,Y(1-r.dev)-5,r.label.replace('->','→'),'font-size="10"');});
    svg+=txt(450,360,variable.replaceAll('_',' '),'text-anchor="middle"')+txt(20,180,'Pair-class development error','text-anchor="middle" transform="rotate(-90 20 180)"');
    $('reuse-plot').innerHTML=svg+'</svg>';
    const rhos=D.correlations[cid(s)][rep(s)];
    $('rho-table').innerHTML=table(['Across pair classes','Spearmanρ','Status'],rhos.map(r=>[r.variable,num(r.spearman_rho),r.status]));
    $('reuse-note').textContent=`${s.k} pair classes; one computational seed (${s.seed}), ${s.roster}/${s.policy}, ${names[s.encoder]}/${names[s.decoder]}. Reuse is extra block draws divided by all block draws, not class frequency or effective sample size. Every class has the same row quota. U2 reuse=0 and R16=.875, so their reuse correlations are undefined. For F16, reuse=1−available_sources/(16×sessions): total support and reuse describe the same association with opposite signs. No p-values or biological confidence intervals are implied. Training and development source reuse are separate.`;
    const policyInfo=Object.fromEntries(['U2','R16','F16'].map(p=>[p,new Map(recallInfo(s,cid(s,s.k,s.roster,p)).map(r=>[r.label,r]))]));
    $('reuse-table').innerHTML=table(['Pair','Available train sources','Used / block draws','Train reuse','Dev used / draws','Train recall','Dev recall','U2 / R16 / F16 dev recall','Frequent mistake'],rs.map(r=>[r.label,r.usage.available_train_sources,r.usage.train_used_sources+' / '+r.usage.train_block_draws,pct(r.usage.train_reuse_fraction),r.usage.development_used_sources+' / '+r.usage.development_block_draws,pct(r.train),pct(r.dev),['U2','R16','F16'].map(p=>pct(policyInfo[p].get(r.label).dev)).join(' / '),r.mistake+' ('+r.mistakeN+')']));
    const policyCut=$('policy-cut').value.split('-'),before=cid(s,s.k,s.roster,policyCut[0]),after=cid(s,s.k,s.roster,policyCut[1]);
    renderChanges('policy-flips',s,before,after);
  }
  function renderChanges(element,s,before,after) {
    const group=D.changes[before+'|'+after]?.[rep(s)];
    if(!group){$(element).innerHTML='<p>Not evaluated for this selection.</p>';return;}
    $(element).innerHTML=table(['Pair','Both right','Wrong→right','Right→wrong','Both wrong','Recall change'],group.map(r=>[r[0],r[1],r[2],r[3],r[4],((r[2]-r[3])*100/8).toFixed(1)+'pp']));
  }
  function sessions(s) {
    if(s.world!=='observed'){$('session-note').textContent='Matched roster changes use observed cases only.';$('session-table').innerHTML='';$('session-flips').innerHTML='';return;}
    const [from,to]=s.cut.split('-'),a=D.grid.find(g=>g.class_count===s.k&&g.roster===from),b=D.grid.find(g=>g.class_count===s.k&&g.roster===to);
    const removed=a.session_aliases.filter(v=>!b.session_aliases.includes(v));
    $('session-note').textContent=`${s.k} classes, ${s.policy}, seed${s.seed}: ${from}→${to} removes${a.sessions-b.sessions} sessions and${a.units-b.units} recorded columns. Removed aliases: ${removed.join(', ')}. The development rows retain exactly the same shared source blocks; models were separately fitted. A change concerns the session group plus refitting, not a causal score for one session. Every constructed row includes every retained session, so session participation alone cannot identify a bad session.`;
    const before=cid(s,s.k,from),after=cid(s,s.k,to);renderChanges('session-flips',s,before,after);
    const original=D.exclusions.filter(r=>r.configuration===`K${s.k}_${from}`),destination=new Map(D.exclusions.filter(r=>r.configuration===`K${s.k}_${to}`).map(r=>[r.session,r]));
    $('session-table').innerHTML=table(['Session alias','Before','After','Destination reason','Standalone session accuracy'],original.map(r=>[r.session,r.included==='True'?'Included':'Excluded',destination.get(r.session).included==='True'?'Included':'Excluded',destination.get(r.session).reason,'Not evaluated']));
  }
  function refresh() {
    const s=state();$('seed').disabled=s.world!=='observed';
    $('context').textContent=`${names[s.encoder]} / ${names[s.decoder]} · ${s.world==='observed'?'observed seed '+s.seed:'diagnostic permutation '+s.world+' (model seed0)'} · whole cue0–1s · exposed, source-separated, label-conditioned development. Class removal, reuse/error and prediction-switch panels always use observed DEVELOPMENT pair predictions, independently of the confusion target and split selectors.`;
    main(s);deletions(s);reuse(s);sessions(s);
  }
  const controls=['k','roster','policy','encoder','decoder','head','seed','world','split','mode','transition','cut','xaxis','policy-cut'];
  controls.forEach(id=>$(id).addEventListener('change',refresh));
  $('grid').addEventListener('click',event=>{
    const target=event.target.closest('button[data-k]');if(!target)return;
    $('k').value=target.dataset.k;$('roster').value=target.dataset.roster;refresh();$('matrix').scrollIntoView({behavior:'smooth',block:'start'});
  });
  $('download').addEventListener('click',()=>{
    const s=state(),m=matrix(s),a=counts(s);if(!a)return;
    const lines=[['true/predicted',...m.labels].join(',')];a.forEach((row,i)=>lines.push([m.labels[i],...row.map(v=>s.mode==='counts'?v:100*v/row.reduce((x,y)=>x+y,0))].join(',')));
    const blob=new Blob([lines.join('\n')+'\n'],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),anchor=document.createElement('a');anchor.href=url;anchor.download=`${cid(s)}_${rep(s)}_${s.head}_${s.split}_${s.mode}.csv`;anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  globalThis.PopulationErrorExplorer={refresh,state,matrixSVG,recallInfo,data:D};
  refresh();
})();
