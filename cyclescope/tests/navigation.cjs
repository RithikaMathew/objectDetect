// Read-only UI regression with API fixtures; never changes saved videos.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 try{
  const page=await browser.newPage({viewport:{width:1200,height:800}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/api/**',async route=>{
   const path=new URL(route.request().url()).pathname;
   const body=path==='/api/dashboard'?{rows:[],sessions:[],references:[],source_manifest:[]}:path==='/api/jobs'?[]:path==='/api/config'?{processing_workers:2}:{id:'navigation-test',name:'Navigation fixture',status:'failed',error:'UI fixture'};
   await route.fulfill({json:body});
  });
  const nav=page.getByRole('navigation',{name:'Main navigation'});
  const check=async(label,id)=>{
   await nav.getByRole('link',{name:label,exact:true}).click();
   await page.waitForFunction(id=>id==='overview'?window.scrollY===0:document.getElementById(id)?.getBoundingClientRect().top<innerHeight,id);
   await nav.locator('a[aria-current=location]').filter({hasText:label}).waitFor();
  };
  await page.goto('http://localhost:5173');
  await check('Analyze','analyze');await check('Video library','library');await check('Overview','overview');
  for(const [label,id] of [['Analyze','analyze'],['Video library','library'],['Overview','overview']]){
   await page.goto('http://localhost:5173/#/job/navigation-test');
   await page.getByText('Navigation fixture',{exact:true}).waitFor();
   await check(label,id);
  }
  await page.evaluate(()=>scrollTo(0,900));await check('Overview','overview');
  await page.goto('http://localhost:5173/#analyze');await page.getByRole('heading',{name:'Analyze a video',exact:true}).waitFor();
  await page.waitForFunction(()=>document.getElementById('analyze').getBoundingClientRect().top<innerHeight);
  await page.setViewportSize({width:390,height:844});
  assert.equal(await nav.getByRole('link',{name:'Video library'}).isVisible(),true);
  await check('Video library','library');
  await page.getByRole('button',{name:'? Ask CycleScope',exact:true}).click();
  await page.getByText('Fixed answers from project notes · no LLM or external API',{exact:true}).waitFor();
  assert.deepEqual(errors,[]);console.log('Navigation passed: home, video page, repeated Overview, deep link, mobile, guide disclosure; no JS errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
