import Http from ".";

// TODO: Not wired yet
export default {
  login(email, password) {
    return Http.post("login", { email, password });
  },
  signUp(email, password) {
    return Http.post("register", { email, password });
  },
};
