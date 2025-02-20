
  
  import { initiateOAuth } from './handlers';
  
  export const OAuthProviders = {
    google: {
      name: 'Google',
      icon: '/google-icon.svg',
      buttonColor: 'bg-white hover:bg-gray-50',
      textColor: 'text-gray-700',
      borderColor: 'border-gray-300',
      initiate: () => initiateOAuth('google')
    },
    github: {
      name: 'GitHub',
      icon: '/github-icon.svg',
      buttonColor: 'bg-gray-900 hover:bg-gray-800',
      textColor: 'text-white',
      borderColor: 'border-transparent',
      initiate: () => initiateOAuth('github')
    }
  };
  
  // OAuth Button Component
  export const OAuthButton = ({ provider, className = '' }) => {
    const providerConfig = OAuthProviders[provider];
    if (!providerConfig) return null;
  
    return (
      <button
        onClick={providerConfig.initiate}
        className={`
          w-full inline-flex justify-center items-center px-4 py-2 
          border ${providerConfig.borderColor} rounded-md shadow-sm 
          text-sm font-medium ${providerConfig.textColor} 
          ${providerConfig.buttonColor} focus:outline-none focus:ring-2 
          focus:ring-offset-2 focus:ring-blue-500 ${className}
        `}
      >
        <img
          src={providerConfig.icon}
          alt={providerConfig.name}
          className="h-5 w-5 mr-2"
        />
        Continue with {providerConfig.name}
      </button>
    );
  };