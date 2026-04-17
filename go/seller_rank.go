package main

import "sort"

func rankSellerOffers(offers []Offer) []Offer {
	sort.Slice(offers, func(i, j int) bool {
		left, right := offers[i], offers[j]
		if left.DeliveryDays != right.DeliveryDays {
			return left.DeliveryDays < right.DeliveryDays
		}
		if left.Stock != right.Stock {
			return left.Stock > right.Stock
		}
		return left.Price < right.Price
	})
	return offers
}
