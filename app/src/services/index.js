import axios from "axios";
import Vue from "vue";

const Http = axios.create({
  baseURL: process.env.VUE_APP_API_URL,
});

// TODO: configure request interceptors

Vue.prototype.$http = Http;

export default Http;
