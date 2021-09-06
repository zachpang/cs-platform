<template>
  <section class="section">
    <div class="container is-max-desktop">
      <div class="columns">
        <div class="column is-one-third is-offset-one-third">
          <h3 class="is-size-3 has-text-weight-bold has-text-centered mb-2">
            Log in
          </h3>
          <div class="box">
            <form @submit.prevent>
              <div class="field">
                <label class="label">Email</label>
                <div class="control">
                  <input
                    v-model="email"
                    class="input"
                    type="email"
                    placeholder="email"
                  />
                </div>
              </div>
              <div class="field">
                <label class="label">Password</label>
                <div class="control">
                  <input
                    v-model="password"
                    class="input"
                    type="password"
                    placeholder="password"
                  />
                </div>
              </div>
              <div class="field">
                <div class="control">
                  <button class="button is-dark is-fullwidth" type="submit">
                    Log in
                  </button>
                </div>
              </div>
            </form>
            <div class="has-text-centered mt-5 pt-3 bt">
              Don't have an account? <router-link to="/">Sign up</router-link>.
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: "Login",
  data() {
    return {
      email: "",
      password: "",
    };
  },
};
</script>

