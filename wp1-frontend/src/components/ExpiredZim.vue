<template>
  <div v-if="zimExpired" class="container text-center mt-5">
    <h1 class="text-danger">ZIM File Expired</h1>
    <p class="lead">Your ZIM file has expired after 2 weeks. Please request a new one.</p>

    <button 
      @click="reRequestZim" 
      :disabled="loading"
      class="btn btn-dark mt-3"
    >
      {{ loading ? 'Processing...' : 'Re-request ZIM' }}
    </button>

    <p v-if="message" class="mt-3 text-success">{{ message }}</p>
    <p v-if="error" class="mt-3 text-danger">{{ error }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      loading: false,
      message: '',
      error: '',
      zimExpired: false, // Track if the ZIM file is expired
    };
  },
  async created() {
    await this.checkZimStatus();
  },
  methods: {
    async checkZimStatus() {
      try {
        const response = await fetch('<WASABI_STORAGE_URL>', { method: 'HEAD' });
        if (!response.ok) {
          this.zimExpired = true; // Show expired message only if file is missing
        }
      } catch (err) {
        console.error('Error checking ZIM file:', err);
        this.zimExpired = true; // Assume expired if request fails
      }
    },
    async reRequestZim() {
      this.loading = true;
      this.message = '';
      this.error = '';

      try {
        // Simulate API request (replace with actual backend request logic)
        await new Promise(resolve => setTimeout(resolve, 1500));

        this.message = 'ZIM request sent successfully! Redirecting...';
        setTimeout(() => {
          this.$router.push('/selections'); 
        }, 2000);
      } catch (err) {
        this.error = 'Failed to send request. Please try again.';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.container {
  max-width: 600px;
  margin: auto;
}
h1 {
  font-size: 2rem;
}
button {
  font-size: 18px;
  padding: 12px 24px;
}
button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>

