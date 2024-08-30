"use client";
import type { RelatedTopic } from "@/app/forum/topic/[topicId]/page";
import { cn } from "@/lib/utils";
import Autoplay from "embla-carousel-autoplay";
import React from "react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "./TestCarousel";
import { Category, Topic, type TopicContent } from "./Topic";

export interface TopicCarouselProps {
  relatedTopics: RelatedTopic[];
  category: Category
}

export function RelatedTopicCarousel({
  relatedTopics,
  category,
}: TopicCarouselProps) {
  const plugin = React.useRef(
    Autoplay({ delay: 3000, stopOnInteraction: true }),
  );

  const isMobile = window?.innerWidth < 768;

  return (
    <Carousel
      plugins={[plugin.current]}
      className="size-full"
      opts={{ align: "start", loop: false }}
    >
      <CarouselContent className="gap-3 ml-0.5">
        {relatedTopics.map((item, index) => {
          if (!item.toTopic.about) return;
          return (
            <CarouselItem
              key={index}
              className={cn(
                "basis-1/1 md:basis-1/3 lg:basis-1/5 pl-0",
                index === relatedTopics.length - 1 && "mr-4",
              )}
            >
              <Topic item={item.toTopic} category={category} />
            </CarouselItem>
          );
        })}
      </CarouselContent>
      {!isMobile && (
        <>
          <CarouselNext className="right-0" />
          <CarouselPrevious className="left-0" />
        </>
      )}
    </Carousel>
  );
}
