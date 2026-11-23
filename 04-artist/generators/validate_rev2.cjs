const validator = require('gltf-validator'); const fs=require('fs');
(async()=>{for (const id of ['b017','b018','b019']) {const buf=fs.readFileSync('../deliverables/tz3_phase_3_1_rev2/'+id+'.glb');let result=await validator.validateBytes(new Uint8Array(buf),{uri:id+'.glb',maxIssues:1000}); console.log(id,JSON.stringify(result.issues,null,2));}})();
