/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */
import * as env from "./env.json";

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: env.auth0.url, // the auth0 domain prefix
    audience: env.auth0.audience, // the audience set for the auth0 app
    clientId: env.auth0.clientId, // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
