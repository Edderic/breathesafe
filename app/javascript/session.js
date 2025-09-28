export async function signIn() {
  if (!this.currentUser) {
    // Prevent re-entrant calls from components that remain alive briefly during route change
    if (this.$route && this.$route.name === 'SignIn') {
      return;
    }

    const currentRoute = this.$route || { name: undefined, params: {}, query: {} };
    const query = JSON.parse(JSON.stringify(currentRoute.query || {}));

    query['attempt-name'] = currentRoute.name;

    for (const key in (currentRoute.params || {})) {
      query[`params-${key}`] = currentRoute.params[key]
    }

    // Defer navigation until after the current component mount completes
    await this.$nextTick();
    await this.$router.replace({
      name: 'SignIn',
      query: query
    })
  }
}
