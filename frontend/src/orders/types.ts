export const orderStatuses = ["pending", "processing", "shipped", "cancelled"] as const;
export type OrderStatus = (typeof orderStatuses)[number];

export type Order = {
  id: string;
  customer_name: string;
  total: string;
  status: OrderStatus;
};
