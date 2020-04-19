import {Page, launch} from 'puppeteer';

export class organizationAction{
    public async origanization(page:Page){
       // const returnBtn = await page.waitForSelector('body > div.lg-layout > header > div.header-right > a:nth-child(1) > button');
       // await returnBtn.click();
            
        const orgBtn = await page.waitForSelector('a[href="#/workspace/contacts"]');
        await orgBtn.click();
        await page.waitFor(3000);

    } 
}
