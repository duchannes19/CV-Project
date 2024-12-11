export const isAuthenticated = () => {
    return !!localStorage.getItem('token');
  };
  
  export const login = async (username, password) => {
    // Simulate server authentication
    if (username && password.length >= 8) {
      localStorage.setItem('token', 'dummy_token');
      return true;
    }
    return false;
  };
  
  export const logout = () => {
    localStorage.removeItem('token');
  };  