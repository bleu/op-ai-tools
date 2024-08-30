"use client";
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
import { Topic, type TopicContent } from "./Topic";

export interface TopicCarouselProps {
  relatedTopics: {
    toTopic: TopicContent;
  }[];
}

export function RelatedTopicCarousel({ relatedTopics }: TopicCarouselProps) {
  const plugin = React.useRef(
    Autoplay({ delay: 3000, stopOnInteraction: true, playOnInit: true }),
  );

  const isMobile = window?.innerWidth < 768;

  return (
    <Carousel
      plugins={[plugin.current]}
      className="size-full"
      opts={{ align: "start", loop: true }}
    >
      <CarouselContent className="gap-3 ml-0.5">
        {relatedTopics.length > 0 ? (
          relatedTopics.map((item, index) => (
            <CarouselItem
              key={index}
              className={cn(
                "basis-1/1 md:basis-1/3 lg:basis-1/5 pl-0",
                index === relatedTopics.length - 1 && "mr-4",
              )}
            >
              <Topic item={item.toTopic} />
            </CarouselItem>
          ))
        ) : (
          <CarouselItem>
            <div className="flex justify-center items-center size-full h-20">
              <span className="text-foreground">No results found.</span>
            </div>
          </CarouselItem>
        )}
      </CarouselContent>
      {!isMobile && (
        <>
          <CarouselNext className="-right-0" />
          <CarouselPrevious className="left-0" />
        </>
      )}
    </Carousel>
  );
}
