import { useRef, useMemo, useState } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import { Box, useColorMode, Spinner, Alert } from '@chakra-ui/react'
import { useContentStore } from '../../store/contentStore'
import type { EventDropArg, EventClickArg } from '@fullcalendar/core'

const getPlatformColor = (platform: string): string => {
  const colors: Record<string, string> = {
    youtube: '#FF0000',
    twitter: '#1DA1F2',
    instagram: '#E4405F',
    facebook: '#1877F2',
    linkedin: '#0A66C2',
    tiktok: '#000000',
    medium: '#000000',
    substack: '#FF6719'
  }
  return colors[platform.toLowerCase()] || '#718096'
}

interface ContentCalendarProps {
  onEventClick?: (variantId: string) => void
}

export const ContentCalendar: React.FC<ContentCalendarProps> = ({ onEventClick }) => {
  const { colorMode } = useColorMode()
  const { contents, updateVariant, isLoading, error } = useContentStore()
  const [updating, setUpdating] = useState(false)
  const calendarRef = useRef<FullCalendar>(null)

  // Transform content variants into calendar events
  const events = useMemo(() => {
    return contents.flatMap((content) =>
      content.variants
        .filter((v) => v.scheduled_for)
        .map((variant) => ({
          id: variant.id,
          title: `${content.title} (${variant.platform})`,
          start: variant.scheduled_for!,
          backgroundColor: getPlatformColor(variant.platform),
          borderColor: getPlatformColor(variant.platform),
          extendedProps: {
            contentId: content.id,
            platform: variant.platform,
            status: content.status,
            platformPostId: variant.platform_post_id
          }
        }))
    )
  }, [contents])

  const handleEventDrop = async (info: EventDropArg) => {
    const { id, extendedProps } = info.event
    const newDate = info.event.start

    if (!newDate) return

    setUpdating(true)
    try {
      // Update the variant's scheduled_for date
      updateVariant(extendedProps.contentId, id, {
        scheduled_for: newDate.toISOString()
      })

      // Here you would typically make an API call
      // await apiClient.updateContentVariant(id, { scheduled_for: newDate.toISOString() })
    } catch (err) {
      console.error('Failed to update event:', err)
      info.revert()
    } finally {
      setUpdating(false)
    }
  }

  const handleEventClick = (info: EventClickArg) => {
    if (onEventClick) {
      onEventClick(info.event.id)
    }
  }

  const handleDateClick = (arg: any) => {
    // Future enhancement: Open create content modal with pre-filled date
    console.log('Date clicked:', arg.dateStr)
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="500px">
        <Spinner size="xl" />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert.Root status="error">
        <Alert.Icon />
        <Alert.Title>{error}</Alert.Title>
      </Alert.Root>
    )
  }

  return (
    <Box
      position="relative"
      sx={{
        '& .fc': {
          fontFamily: 'inherit'
        },
        '& .fc-toolbar-title': {
          fontSize: '1.5rem',
          fontWeight: 'bold',
          color: colorMode === 'dark' ? 'white' : 'gray.800'
        },
        '& .fc-button': {
          backgroundColor: colorMode === 'dark' ? 'gray.700' : 'blue.500',
          borderColor: colorMode === 'dark' ? 'gray.600' : 'blue.600',
          color: 'white',
          '&:hover': {
            backgroundColor: colorMode === 'dark' ? 'gray.600' : 'blue.600'
          },
          '&:disabled': {
            opacity: 0.5
          }
        },
        '& .fc-button-active': {
          backgroundColor: colorMode === 'dark' ? 'gray.600' : 'blue.700'
        },
        '& .fc-daygrid-day': {
          backgroundColor: colorMode === 'dark' ? 'gray.800' : 'white'
        },
        '& .fc-day-today': {
          backgroundColor: colorMode === 'dark' ? 'gray.700' : 'blue.50'
        },
        '& .fc-event': {
          cursor: 'pointer',
          fontSize: '0.85rem'
        },
        '& .fc-col-header-cell': {
          backgroundColor: colorMode === 'dark' ? 'gray.700' : 'gray.100',
          color: colorMode === 'dark' ? 'white' : 'gray.700'
        }
      }}
    >
      {updating && (
        <Box
          position="absolute"
          top={4}
          right={4}
          zIndex={1000}
          padding={2}
          borderRadius="md"
          backgroundColor="blue.500"
          color="white"
        >
          Updating...
        </Box>
      )}

      <FullCalendar
        ref={calendarRef}
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay'
        }}
        events={events}
        editable={true}
        droppable={true}
        eventDrop={handleEventDrop}
        eventClick={handleEventClick}
        dateClick={handleDateClick}
        height="auto"
        nowIndicator={true}
        eventTimeFormat={{
          hour: '2-digit',
          minute: '2-digit',
          meridiem: 'short'
        }}
        slotLabelFormat={{
          hour: '2-digit',
          minute: '2-digit',
          meridiem: 'short'
        }}
      />
    </Box>
  )
}
