import axios from 'axios';
import { config } from 'dotenv';
import path from 'path';




const YAHOO_OAUTH_URL = 'https://api.login.yahoo.com/oauth2/get_token';
const YAHOO_AUTH_URL = 'https://api.login.yahoo.com/oauth2/request_auth';
console.log(path.resolve(__dirname, '.env.local'));

const createOAuthParams = (): URLSearchParams => {
    if (!process.env.YAHOO_CLIENT_ID) {
        throw new Error('YAHOO_CLIENT_ID is not defined');
      }
    const clientId: string = process.env.YAHOO_CLIENT_ID;
    const params = new URLSearchParams();
    if (clientId) {
      params.append('client_id', clientId);
    } else {
      throw new Error('Client ID is undefined');
    }
  
    params.append('response_type', 'code');
    params.append('redirect_uri', 'https://localhost.com:3000/callback');
    params.append('scope', 'openid profile email');
  
    return params;
  };

export const getYahooAccessToken = async () => {
  const clientSecret: string | undefined = process.env.YAHOO_CLIENT_SECRET;
  const params = createOAuthParams();

  if (clientSecret) {
	params.append('client_secret', clientSecret);
  } else {
	throw new Error('Client Secret is undefined');
  }

  try {
	const response = await axios.post(YAHOO_OAUTH_URL, params, {
	  headers: {
		'Content-Type': 'application/x-www-form-urlencoded',
	  },
	});
	return response.data.access_token;
  } catch (error) {
	console.error('Error obtaining Yahoo access token:', error);
	throw error;
  }
};

export const getAuthorizationUrl = () => {
  const params = createOAuthParams();
  return `${YAHOO_AUTH_URL}?${params.toString()}`;
};