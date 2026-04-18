package main

import "sort"

func rankMarketOffers(offers []Offer) []Offer {
	sort.Slice(offers, func(i, j int) bool {
		left, right := offers[i], offers[j]
		if left.Price != right.Price {
			return left.Price < right.Price
		}
		if left.SellerRating != right.SellerRating {
			return left.SellerRating > right.SellerRating
		}
		if left.DeliveryDays != right.DeliveryDays {
			return left.DeliveryDays < right.DeliveryDays
		}
		return left.Stock > right.Stock
	})
	return offers
}
