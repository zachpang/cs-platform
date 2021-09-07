import authenticationService from "@/services/authentication.js";
/*
  Equivalent to 'data'
  vuex/store's state object. The object to be used as global/application's state
*/
const state = {
  profile: {},
};

/*
  Equivalent to 'computed properties'
  Computations on state are cached and are reactive to state changes.
*/
const getters = {};

/*
  Keep private
  setters/mutates state. Mutations must be synchronous to enable logging/tracking state in debugger
*/
const mutations = {
  SET_PROFILE(state, profile) {
    state.profile = profile;
  },
};

/*
  Equivalent to 'methods'
  Asynchronous operations (e.g. over network). Once completed, calls mutations to set global state
*/
const actions = {
  async login({ commit }, { email, password }) {},
};

export default {
  state,
  getters,
  mutations,
  actions,
};
