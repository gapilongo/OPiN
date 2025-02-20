

export const initiateOAuth = (provider) => {
  // Generate random state for security
  const state = btoa(JSON.stringify({
    provider,
    nonce: Math.random().toString(36).substring(2)
  }));

  // Store state in session storage for verification
  sessionStorage.setItem('oauthState', state);

  // Get provider config
  const config = getProviderConfig(provider);

  // Build OAuth URL
  const url = new URL(config.authorizationUrl);
  url.searchParams.append('client_id', config.clientId);
  url.searchParams.append('redirect_uri', config.redirectUri);
  url.searchParams.append('scope', config.scope);
  url.searchParams.append('state', state);
  url.searchParams.append('response_type', 'code');

  // Redirect to OAuth provider
  window.location.href = url.toString();
};

const getProviderConfig = (provider) => {
  const configs = {
    google: {
      authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
      clientId: process.env.GOOGLE_CLIENT_ID,
      redirectUri: `${window.location.origin}/auth/oauth/callback`,
      scope: 'openid email profile'
    },
    github: {
      authorizationUrl: 'https://github.com/login/oauth/authorize',
      clientId: process.env