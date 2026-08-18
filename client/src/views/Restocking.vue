<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="orderSuccess" class="success-banner">
      <span>{{ t('restocking.orderSuccess', { orderNumber: orderSuccess.order_number }) }}</span>
      <button class="dismiss-button" @click="orderSuccess = null">{{ t('restocking.dismiss') }}</button>
    </div>

    <div v-if="orderError" class="error">{{ orderError }}</div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="recommendations">
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budgetCard.title') }}</h3>
          <span class="budget-readout">{{ currencySymbol }}{{ budget.toLocaleString() }}</span>
        </div>
        <input
          v-model.number="budget"
          type="range"
          min="0"
          max="50000"
          step="500"
          class="budget-slider"
          @change="loadRecommendations"
        />
        <div class="budget-range-labels">
          <span>{{ currencySymbol }}0</span>
          <span>{{ currencySymbol }}50,000</span>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.stats.totalRecommendedCost') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ recommendations.total_recommended_cost.toLocaleString() }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.stats.remainingBudget') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ recommendations.remaining_budget.toLocaleString() }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.stats.itemsFunded') }}</div>
          <div class="stat-value">{{ fundedItems.length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendationsTitle') }} ({{ recommendations.items.length }})</h3>
          <button
            class="primary-button"
            :disabled="fundedItems.length === 0"
            @click="showPlaceOrderModal = true"
          >
            {{ t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="recommendations.items.length === 0" class="no-items">
          {{ t('restocking.noItemsFunded') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.warehouse') }}</th>
                <th>{{ t('restocking.table.category') }}</th>
                <th>{{ t('restocking.table.quantityOnHand') }}</th>
                <th>{{ t('restocking.table.reorderPoint') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th>{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.table.recommendedQuantity') }}</th>
                <th>{{ t('restocking.table.recommendedCost') }}</th>
                <th>{{ t('restocking.table.urgencyScore') }}</th>
                <th>{{ t('restocking.table.status') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in recommendations.items"
                :key="item.sku"
                :class="{ 'unfunded-row': !item.funded }"
              >
                <td><strong>{{ item.sku }}</strong></td>
                <td>{{ translateProductName(item.item_name) }}</td>
                <td>{{ translateWarehouse(item.warehouse) }}</td>
                <td>{{ translateCategory(item.category) }}</td>
                <td>{{ item.quantity_on_hand }}</td>
                <td>{{ item.reorder_point }}</td>
                <td>
                  <span :class="['badge', item.trend]">
                    {{ t(`trends.${item.trend}`) }}
                  </span>
                </td>
                <td>{{ currencySymbol }}{{ item.unit_cost.toFixed(2) }}</td>
                <td><strong>{{ item.recommended_quantity }}</strong></td>
                <td>{{ currencySymbol }}{{ item.recommended_cost.toLocaleString() }}</td>
                <td>{{ item.urgency_score.toFixed(1) }}</td>
                <td>
                  <span :class="['badge', item.funded ? 'success' : 'danger']">
                    {{ item.funded ? t('restocking.status.funded') : t('restocking.status.unfunded') }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <PlaceOrderModal
      :is-open="showPlaceOrderModal"
      :items="fundedItems"
      :total-cost="fundedTotalCost"
      @close="showPlaceOrderModal = false"
      @confirm="confirmOrder"
    />
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import PlaceOrderModal from '../components/PlaceOrderModal.vue'

export default {
  name: 'Restocking',
  components: {
    PlaceOrderModal
  },
  setup() {
    const { t, currentCurrency, translateProductName, translateWarehouse } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })

    const loading = ref(true)
    const error = ref(null)
    const recommendations = ref(null)
    const budget = ref(5000)

    const showPlaceOrderModal = ref(false)
    const orderError = ref(null)
    const orderSuccess = ref(null)

    // Restocking doesn't support month/status filters, only warehouse and category
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    const fundedItems = computed(() => {
      return recommendations.value ? recommendations.value.items.filter(item => item.funded) : []
    })

    const fundedTotalCost = computed(() => {
      return fundedItems.value.reduce((sum, item) => sum + item.recommended_cost, 0)
    })

    const loadRecommendations = async () => {
      try {
        loading.value = true
        error.value = null
        const filters = getCurrentFilters()
        recommendations.value = await api.getRestockingRecommendations(budget.value, {
          warehouse: filters.warehouse,
          category: filters.category
        })
      } catch (err) {
        error.value = 'Failed to load restocking recommendations: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Watch shared warehouse/category filters and refetch on change.
    // Budget is refetched separately via the slider's @change handler
    // (not a watcher) so dragging doesn't trigger a request per tick.
    watch([selectedLocation, selectedCategory], () => {
      loadRecommendations()
    })

    const translateCategory = (category) => {
      const categoryMap = {
        'Circuit Boards': t('categories.circuitBoards'),
        'Sensors': t('categories.sensors'),
        'Actuators': t('categories.actuators'),
        'Controllers': t('categories.controllers'),
        'Power Supplies': t('categories.powerSupplies')
      }
      return categoryMap[category] || category
    }

    const confirmOrder = async () => {
      orderError.value = null
      try {
        const payload = {
          budget: budget.value,
          items: fundedItems.value.map(item => ({
            sku: item.sku,
            item_name: item.item_name,
            quantity: item.recommended_quantity,
            unit_cost: item.unit_cost
          }))
        }
        const order = await api.createRestockingOrder(payload)
        orderSuccess.value = order
        showPlaceOrderModal.value = false
      } catch (err) {
        orderError.value = 'Failed to place restocking order: ' + err.message
      }
    }

    onMounted(loadRecommendations)

    return {
      t,
      loading,
      error,
      recommendations,
      budget,
      fundedItems,
      fundedTotalCost,
      loadRecommendations,
      showPlaceOrderModal,
      orderError,
      orderSuccess,
      confirmOrder,
      currencySymbol,
      translateProductName,
      translateWarehouse,
      translateCategory
    }
  }
}
</script>

<style scoped>
.budget-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.budget-readout {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.budget-slider {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: #e2e8f0;
  appearance: none;
  outline: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  border: 3px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  cursor: pointer;
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  border: 3px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  cursor: pointer;
}

.budget-range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.813rem;
  color: #64748b;
}

.primary-button {
  padding: 0.625rem 1.25rem;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease;
  font-family: inherit;
  white-space: nowrap;
}

.primary-button:hover:not(:disabled) {
  transform: translateY(-2px);
}

.primary-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.unfunded-row {
  opacity: 0.55;
}

.no-items {
  padding: 2rem;
  text-align: center;
  color: #64748b;
}

.success-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: #d1fae5;
  border: 1px solid #6ee7b7;
  color: #065f46;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.938rem;
  font-weight: 500;
}

.dismiss-button {
  background: none;
  border: none;
  color: #065f46;
  font-weight: 600;
  text-decoration: underline;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.875rem;
  flex-shrink: 0;
}
</style>
