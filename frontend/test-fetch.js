fetch('https://pub-125c1e42244548b0a2dbb3e14415315f.r2.dev/data.json')
  .then(res => console.log('Status:', res.status, res.headers.get('server')))
  .catch(err => console.error(err));
