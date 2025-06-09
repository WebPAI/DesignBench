
<script setup lang="ts">
import { ArrowRight } from 'lucide-vue-next';
</script>

<template>
  <section class="w-full py-16 bg-[#f5f1ea] dark:bg-black">
    <div class="container mx-auto px-4 max-w-6xl">
      <h2 class="text-4xl md:text-5xl font-serif text-center text-stone-600 dark:text-stone-200 mb-4">Services offered</h2>
      <p class="text-center text-stone-700 dark:text-stone-300 mb-16 max-w-3xl mx-auto">
        Explore tailored solutions designed to enhance your business visibility at soug.
      </p>

      <div class="grid md:grid-cols-3 gap-6">
        <!-- Store Customization -->
        <div class="relative overflow-hidden rounded-sm group">
          <div class="absolute inset-0 bg-black/40 z-10"></div>
          <img
            src="/placeholder.svg"
            alt="Store customization"
            width="400"
            height="600"
            class="w-full h-[400px] object-cover"
          />
          <div class="absolute inset-0 z-20 p-8 flex flex-col justify-between text-white">
            <div>
              <h3 class="text-2xl md:text-3xl font-serif mb-2 text-center">
                STORE
                <br />
                CUSTOMIZATION
              </h3>
              <p class="mt-4 text-center">
                Transform your online store with our user-friendly tools that allow for personalized design and
                functionality, ensuring your brand stands out.
              </p>
            </div>
            <div class="text-center">
              <a href="#" class="inline-flex items-center text-white hover:underline">
                Contact <ArrowRight class="ml-2 h-4 w-4" />
              </a>
            </div>
          </div>
        </div>

        <!-- Targeted Marketing -->
        <div class="relative overflow-hidden rounded-sm group">
          <div class="absolute inset-0 bg-black/40 z-10"></div>
          <img
            src="/placeholder.svg"
            alt="Targeted marketing"
            width="400"
            height="600"
            class="w-full h-[400px] object-cover"
          />
          <div class="absolute inset-0 z-20 p-8 flex flex-col justify-between text-white">
            <div>
              <h3 class="text-2xl md:text-3xl font-serif mb-2 text-center">
                TARGETED
                <br />
                MARKETING
              </h3>
              <p class="mt-4 text-center">
                Leverage our marketing expertise to reach your ideal customers, enhancing visibility and driving
                traffic to your store.
              </p>
            </div>
            <div class="text-center">
              <a href="#" class="inline-flex items-center text-white hover:underline">
                Contact <ArrowRight class="ml-2 h-4 w-4" />
              </a>
            </div>
          </div>
        </div>

        <!-- Seamless Delivery -->
        <div class="relative overflow-hidden rounded-sm group">
          <div class="absolute inset-0 bg-black/40 z-10"></div>
          <img
            src="/placeholder.svg"
            alt="Seamless delivery"
            width="400"
            height="600"
            class="w-full h-[400px] object-cover"
          />
          <div class="absolute inset-0 z-20 p-8 flex flex-col justify-between text-white">
            <div>
              <h3 class="text-2xl md:text-3xl font-serif mb-2 text-center">SEAMLESS DELIVERY</h3>
              <p class="mt-4 text-center">
                Offer your customers reliable delivery options, ensuring their purchases arrive promptly and securely
                at their doorstep.
              </p>
            </div>
            <div class="text-center">
              <a href="#" class="inline-flex items-center text-white hover:underline">
                Contact <ArrowRight class="ml-2 h-4 w-4" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
