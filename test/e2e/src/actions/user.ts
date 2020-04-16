import {Page} from 'puppeteer'

export class UserAction{


    public async login(page:Page, username:string, password:string){

        const usernameInput = await page.waitForSelector('input[type = "text"]');
        await usernameInput.type(username);
        const passwordInput = await page.waitForSelector('input[type = "password"]');
        await passwordInput.type(password);
        
        const loginBtn = await page.waitForSelector('button[type = "button"]');
        await loginBtn.click();
        
        console.log("login success");
        await page.waitFor(3000);

    }


}
