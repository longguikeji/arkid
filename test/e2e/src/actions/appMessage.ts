import {Page, launch} from 'puppeteer';

export class appMessageAction{
    public async appinformation(page:Page){
        
        await page.waitFor(3000);
        await page.waitForSelector('.card-list.flex-row>li');
        const apps = await page.$$('.card-list.flex-row>li');
        const appsVal = await page.$$eval('.card-list.flex-row>li',eles=>(eles.map(ele=>ele.textContent)));
        console.log('apps ==',appsVal);
    }
}
