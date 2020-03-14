import {Page} from 'puppeteer'
import cofig from '../config';

export class UserAction{


    public async login(page:Page, username:string, password:string){
   
        await page.goto(cofig.url);


        const usernameInput = await page.waitForSelector('input[type = "text"]');
        await usernameInput.type(username);
        const passwordInput = await page.waitForSelector('input[type = "password"]');
        await passwordInput.type(password);
        

        const loginBtn = await page.waitForSelector('button[type = "button"]');
        await loginBtn.click();

    }


}